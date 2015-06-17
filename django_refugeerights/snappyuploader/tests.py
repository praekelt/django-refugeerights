from django.test import TestCase
from django.test.utils import override_settings
import responses
import json
from .models import SnappyFaq
from .tasks import sync_faqs, csv_importer


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
                            "order": 0},
                           {"id": 2223,
                            "account_id": 12345,
                            "title": "Refugee FAQ 2223",
                            "url": "refugee-rights-2",
                            "custom_theme": "",
                            "culture": "en",
                            "navigation": "{Nav}",
                            "created_at": "2013-11-16 19:14:17",
                            "updated_at": "2013-11-19 07:46:59",
                            "order": 1}]

        responses.add(responses.GET,
                      "https://app.besnappy.com/api/v1/account/12345/faqs",
                      json.dumps(snappy_response),
                      status=200, content_type='application/json')

        sync_result = sync_faqs.delay()

        faqs = SnappyFaq.objects.all()
        self.assertEqual(len(faqs), 3)
        self.assertEqual(sync_result.get(),
                         "FAQs synced. Created FAQs: Refugee FAQ 2222\n"
                         "Refugee FAQ 2223\n")

    @responses.activate
    def test_sync_faqs_no_new(self):
        snappy_response = [{"id": 1,
                            "account_id": 12345,
                            "title": "Test FAQ",
                            "url": "already-in-database",
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

        sync_result = sync_faqs.delay()

        faqs = SnappyFaq.objects.all()
        self.assertEqual(len(faqs), 1)
        self.assertEqual(sync_result.get(), "FAQs synced. Created FAQs: ")


class SnappyCSVUploadTest(TestCase):
    fixtures = ["test_snappyuploader.json"]

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory',)
    def setUp(self):
        super(SnappyCSVUploadTest, self).setUp()

    def test_data_loaded(self):
        faqs = SnappyFaq.objects.all()
        self.assertEqual(len(faqs), 1)

    @responses.activate
    def test_upload_csv(self):
        api_root = "https://app.besnappy.com/api/v1/account/12345"
        snappy_topics_response = [
            {
                "id": 52,
                "faq_id": 2222,
                "topic": "Stuff",
                "order": 0,
                "created_at": "2014-01-08 02:15:05",
                "updated_at": "2014-01-08 02:15:05",
                "slug": "stuff"
            },
            {
                "id": 240,
                "faq_id": 2222,
                "topic": "Nonsense",
                "order": 0,
                "created_at": "2014-01-08 02:15:09",
                "updated_at": "2014-01-08 02:15:09",
                "slug": "nonsense"
            }
        ]

        responses.add(responses.GET,
                      "%s/faqs/2222/topics" % api_root,
                      json.dumps(snappy_topics_response),
                      status=200, content_type='application/json')
        csv_dict = {}
        import_result = csv_importer.delay(csv_dict, 2222)

        self.assertEqual(import_result.get(),
                         "Topics found: 2")
