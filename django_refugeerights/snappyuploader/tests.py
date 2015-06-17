from django.test import TestCase
from django.test.utils import override_settings
import responses
import json
from .models import SnappyFaq
from .tasks import sync_faqs


class SnappyFaqSyncTest(TestCase):
    fixtures = ["test_snappyuploader.json"]

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory',)
    def setUp(self):
        super(SnappyFaqSyncTest, self).setUp()

    def test_data_loaded(self):
        faqs = SnappyFaq.objects.all()
        self.assertEqual(len(faqs), 1)

    @responses.activate
    def test_sync_faqs(self):
        snappy_response = [{"id": 2222,
                            "account_id": 12345,
                            "title": "Refugee FAQ 2222",
                            "url": "refugee-rights",
                            "custom_theme": "",
                            "culture": "en",
                            "navigation": "{Nav}",
                            "created_at": "2013-11-16 19:14:17",
                            "updated_at": "2013-11-19 07:46:59",
                            "order": 0}]

        responses.add(responses.GET,
                      "https://app.besnappy.com/api/v1/account/12345/faqs",
                      json.dumps(snappy_response),
                      status=200, content_type='application/json')

        sync_result = sync_faqs()

        faqs = SnappyFaq.objects.all()
        self.assertEqual(len(faqs), 2)
        self.assertEqual(sync_result, "")
