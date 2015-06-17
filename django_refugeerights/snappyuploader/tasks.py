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
        row = 0
        try:
            # Get FAQ topics
            topics = snappy_request(
                "GET",
                "account/%s/faqs/%s/topics" % (
                    settings.SNAPPY_ACCOUNT_ID, faq_id, ))
            return "Topics found: %s" % len(topics)
            # for line in poidata:
            #     row += 1
            #     if "Latitude" in line and "Longitude" in line:
            #         if line["Longitude"] != "" and line["Latitude"] != "":
            #             poi_point = Point(float(line["Longitude"]),
            #                               float(line["Latitude"]))
            #             # check if point exists
            #             locations = Location.objects.filter(point=poi_point)
            #             if locations.count() == 0:
            #                 # make a Location
            #                 location = Location()
            #                 location.point = poi_point
            #                 location.save()
            #             else:
            #                 # Grab the top of the stack
            #                 location = locations[0]
            #             # Create new point of interest with location
            #             poi = PointOfInterest()
            #             poi.location = location
            #             poi.data = line
            #             poi.save()
            #             imported += 1
            #             l.info("Imported: %s" % line["Clinic Name"])
            #         else:
            #             l.info(
            #                 "Row <%s> has corrupted point data, "
            #                 "not imported" % row)
            #     else:
            #         l.info("Row <%s> missing point data, not imported" % row)
            # l.info("Imported <%s> locations" % str(imported))
            # return imported
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
