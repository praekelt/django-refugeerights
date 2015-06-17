from celery import task
from django.conf import settings
import requests
from .models import SnappyFaq


def snappy_request(method, endpoint):
    """
    Function that makes the Snappy Api requests.
    """
    api_url = "%s/%s" % (settings.SNAPPY_BASE_URL, endpoint)
    auth = (settings.SNAPPY_API_KEY, 'x')
    headers = {'content-type': 'application/json; charset=utf-8'}

    if method == "GET":
        response = requests.get(api_url, auth=auth, headers=headers)

    return response.json()


@task()
def sync_faqs():
    """
    Task that reads the FAQ list from the refugee rights Snappy account and
    adds any new FAQs to the database.
    """

    # Get the FAQs via the Snappy Api
    response = snappy_request("GET",
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
