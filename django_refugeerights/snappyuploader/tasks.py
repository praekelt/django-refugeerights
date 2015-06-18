from __future__ import absolute_import

from celery.task import Task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
import requests

from django.conf import settings

from .models import SnappyFaq

import json

logger = get_task_logger(__name__)


def snappy_request(method, endpoint, py_data=None):
    """
    Function that makes the Snappy Api requests.
    """
    api_url = "%s/%s" % (settings.SNAPPY_BASE_URL, endpoint)
    auth = (settings.SNAPPY_API_KEY, 'x')
    headers = {'content-type': 'application/json; charset=utf-8'}
    if method is "POST":
        data = json.dumps(py_data)
        response = requests.post(
            api_url, auth=auth, data=data, headers=headers, verify=False)
    elif method == "GET":
        response = requests.get(
            api_url, auth=auth, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()


class Post_FAQ(Task):

    """
    Task to add an FAQ entry to Snappy via Api post
    """
    name = "snappyuploader.tasks.post_faq"

    def run(self, topic_id, faq_id, data, **kwargs):
        """
        Returns FAQ id of imported FAQ
        """
        response = snappy_request(
            "POST",
            "account/%s/faqs/%s/topics/%s/questions" % (
                settings.SNAPPY_ACCOUNT_ID, faq_id, topic_id),
            py_data=data)

        return "Uploaded FAQ %s" % response["id"]

post_faq = Post_FAQ()


class CSV_Importer(Task):

    """
    Task to take dict import the data
    """
    name = "snappyuploader.tasks.csv_importer"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return
        code.
        """

    def run(self, csv_data, faq_id, **kwargs):
        """
        Returns count of imported faqs
        """
        l = self.get_logger(**kwargs)

        l.info("Processing new snappy FAQ import data")
        imported = 0
        failed_imports = 0
        try:
            # Get FAQ topics
            snappy_topics_data = snappy_request(
                "GET",
                "account/%s/faqs/%s/topics" % (
                    settings.SNAPPY_ACCOUNT_ID, faq_id, ))
            # Save the topics in a reusable dict {topic1: id1, topic2: id2,}
            topics_map = {}
            for snappy_topic_obj in snappy_topics_data:
                topics_map[snappy_topic_obj["topic"]] = snappy_topic_obj["id"]

            # Upload the CSV entries line by line
            for csv_entry in csv_data:
                topic_title = csv_entry["topic"]
                if topic_title in topics_map:
                    topic_id = topics_map[topic_title]
                else:
                    # Post new topic to snappy
                    data = {"topic": topic_title}
                    response = snappy_request(
                        "POST",
                        "account/%s/faqs/%s/topics" % (
                            settings.SNAPPY_ACCOUNT_ID, faq_id),
                        py_data=data)
                    # Set topic_id to new topic id
                    topic_id = response["id"]
                    # Add new topic to topics_map
                    topics_map[topic_title] = topic_id

                # Post new FAQ
                data = {"question": csv_entry["question"],
                        "answer": csv_entry["answer"]}
                try:
                    post_faq.delay(topic_id, faq_id, data)
                    imported += 1
                except:
                    logger.error('Failed to upload question: %s' % (
                        csv_entry["question"]))
                    failed_imports += 1

            return "FAQs added: %s. Failed uploads: %s" % (imported,
                                                           failed_imports)

        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing location import \
                 via Celery.',
                exc_info=True)

csv_importer = CSV_Importer()


class Sync_FAQs(Task):

    """
    Task that reads the FAQ list from the refugee rights Snappy account and
    adds any new FAQs to the database.
    """
    name = "snappyuploader.tasks.sync_faqs"

    def run(self, **kwargs):
        # Get the FAQs via the Snappy Api
        try:
            response = snappy_request(
                "GET",
                "account/%s/faqs" % settings.SNAPPY_ACCOUNT_ID)

            # Check if the FAQs exist and create entries in DB if not
            created_faqs = ""
            for faq in response:
                obj, created = SnappyFaq.objects.get_or_create(
                    snappy_id=int(faq["id"]),
                    name=faq["title"])
                if created:
                    created_faqs += obj.name + "\n"
            return u"FAQs synced. Created FAQs: %s" % created_faqs
        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing location import \
                 via Celery.',
                exc_info=True)

sync_faqs = Sync_FAQs()
