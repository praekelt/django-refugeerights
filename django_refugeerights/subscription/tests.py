import json
import logging

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from djcelery.models import PeriodicTask
from go_http.send import LoggingSender

from subscription.models import Subscription
from contentstore.models import MessageSet
from subscription.tasks import (process_message_queue, processes_message)


# Tests that the subscription application has been installed and routed to


class APITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()


class AuthenticatedAPITestCase(APITestCase):

    def setUp(self):
        super(AuthenticatedAPITestCase, self).setUp()
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(self.username,
                                             'testuser@example.com',
                                             self.password)
        token = Token.objects.create(user=self.user)
        self.token = token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)


class TestSubscription(AuthenticatedAPITestCase):

    fixtures = ["test"]

    def test_data_loaded(self):
        messagesets = MessageSet.objects.all()
        self.assertEqual(len(messagesets), 2)
        subscriptions = Subscription.objects.all()
        self.assertEqual(len(subscriptions), 3)

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.schedule = PeriodicTask.objects.create()

    def test_login(self):
        request = self.client.post(
            '/api-token-auth/',
            {"username": "testuser", "password": "testpass"})
        token = request.data.get('token', None)
        self.assertIsNotNone(
            token, "Could not receive authentication token on login post.")
        self.assertEqual(request.status_code, 200,
                         "Status code on /auth/login was %s (should be 200)."
                         % request.status_code)

    def test_create_subscription(self):
        post_data = {
            'contact_key': 'kjdlkjsldfoiuwerwe',
            'to_addr': '+27845001001',
            'messageset_id': '1',
            'lang': 'en_GB',
            'schedule': self.schedule.id
        }
        response = self.client.post('/subscription/subscription/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Subscription.objects.last()
        self.assertEqual(d.contact_key, "kjdlkjsldfoiuwerwe")
        self.assertEqual(d.to_addr, "+27845001001")
        self.assertEqual(d.messageset_id, 1)
        self.assertEqual(d.lang, "en_GB")
        self.assertEqual(d.schedule.id, self.schedule.id)

    def test_switch_subscription(self):
        post_data = {
            'contact_key': '82309423098',
            'messageset_id': '1',
            'schedule': self.schedule.id
        }

        self.assertEqual(Subscription.objects.filter(
            contact_key='82309423098',
            active=True, completed=False).count(), 3)

        response = self.client.post('/subscription/switch_subscription/',
                                    json.dumps(post_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = Subscription.objects.last()
        self.assertEqual(d.contact_key, "82309423098")
        self.assertEqual(d.messageset_id, 1)
        self.assertEqual(d.schedule.id, self.schedule.id)

        self.assertEqual(Subscription.objects.filter(
            contact_key='82309423098',
            active=True, completed=False).count(), 1)

    def test_get_unfiltered_subscription(self):
        response = self.client.get('/subscription/subscription/',
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_get_filtered_subscription(self):
        response = self.client.get('/subscription/subscription/',
                                   {"to_addr": "+278888"},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_patch_subscription(self):
        response = self.client.get('/subscription/subscription/',
                                   {"to_addr": "+278888"},
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        sub = response.data[0]
        self.assertEqual(sub["active"], True)
        patch_data = {"active": False}
        patch = self.client.patch('/subscription/subscription/%s/' % sub["id"],
                                  json.dumps(patch_data),
                                  content_type='application/json')
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["active"], False)
        d = Subscription.objects.get(id=sub["id"])
        self.assertEqual(d.active, False)


class RecordingHandler(logging.Handler):

    """ Record logs. """
    logs = None

    def emit(self, record):
        if self.logs is None:
            self.logs = []
        self.logs.append(record)


class TestMessageQueueProcessor(TestCase):

    fixtures = ["test"]

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory',)
    def setUp(self):
        self.sender = LoggingSender('go_http.test')
        self.handler = RecordingHandler()
        logger = logging.getLogger('go_http.test')
        logger.setLevel(logging.INFO)
        logger.addHandler(self.handler)

    def check_logs(self, msg):
        if type(self.handler.logs) != list:
            [logs] = self.handler.logs
        else:
            logs = self.handler.logs
        for log in logs:
            if log.msg == msg:
                return True
        return False

    def test_data_loaded(self):
        messagesets = MessageSet.objects.all()
        self.assertEqual(len(messagesets), 2)
        subscriptions = Subscription.objects.all()
        self.assertEqual(len(subscriptions), 3)

    def test_multisend(self):
        schedule = 1
        result = process_message_queue.delay(schedule, self.sender)
        self.assertEquals(result.get(), 3)
        self.assertEquals(
            True,
            self.check_logs(
                "Metric: 'sum.sms.subscription.outbound' [sum] -> 3"))

    def test_multisend_none(self):
        schedule = 2
        result = process_message_queue.delay(schedule, self.sender)
        self.assertEquals(result.get(), 0)

    def test_send_message_1_en_first(self):
        subscription = Subscription.objects.get(pk=1)
        result = processes_message.delay(subscription.id, self.sender)
        self.assertEqual(result.get(), {
            "message_id": result.get()["message_id"],
            "to_addr": "+271234",
            "content": "Message 1 on first",
        })
        subscriber_updated = Subscription.objects.get(pk=1)
        self.assertEquals(subscriber_updated.next_sequence_number, 2)
        self.assertEquals(subscriber_updated.process_status, 0)

    def test_next_message_2_post_send_en_first(self):
        subscription = Subscription.objects.get(pk=1)
        result = processes_message.delay(subscription.id, self.sender)
        self.assertTrue(result.successful())
        subscriber_updated = Subscription.objects.get(pk=1)
        self.assertEquals(subscriber_updated.next_sequence_number, 2)

    def test_set_completed_post_send_en_first_2(self):
        subscription = Subscription.objects.get(pk=1)
        subscription.next_sequence_number = 2
        subscription.save()
        result = processes_message.delay(subscription.id, self.sender)
        self.assertTrue(result.successful())
        subscriber_updated = Subscription.objects.get(pk=1)
        self.assertEquals(subscriber_updated.completed, True)
        self.assertEquals(subscriber_updated.active, False)

    def test_new_subscription_created_post_send_en_first_2(self):
        subscription = Subscription.objects.get(pk=1)
        subscription.next_sequence_number = 2
        subscription.save()
        result = processes_message.delay(subscription.id, self.sender)
        self.assertTrue(result.successful())
        # Check another added and old still there
        all_subscription = Subscription.objects.all()
        self.assertEquals(len(all_subscription), 4)
        # Check new subscription is for second
        new_subscription = Subscription.objects.last()
        self.assertEquals(new_subscription.messageset_id, 2)
        self.assertEquals(new_subscription.to_addr, "+271234")
        # make sure the new sub is on a different schedule
        periodictask = PeriodicTask.objects.get(pk=2)
        self.assertEquals(new_subscription.schedule, periodictask)
        # Check finished_messages metric not fired
        self.assertEquals(
            False,
            self.check_logs("Metric: 'sum.finished_messages' [sum] -> 1"))
        self.assertEquals(
            True,
            self.check_logs("Metric: 'sum.1_completed' [sum] -> 1"))

    def test_no_new_subscription_created_post_send_en_second_2(self):
        subscription = Subscription.objects.get(pk=2)
        result = processes_message.delay(subscription.id, self.sender)
        self.assertTrue(result.successful())
        # Check no new subscription added
        all_subscription = Subscription.objects.all()
        self.assertEquals(len(all_subscription), 3)
        # Check old one now inactive and complete
        subscriber_updated = Subscription.objects.get(pk=2)
        self.assertEquals(subscriber_updated.completed, True)
        self.assertEquals(subscriber_updated.active, False)
        # Check finished_messages metric fired
        self.assertEquals(
            True,
            self.check_logs("Metric: 'sum.finished_messages' [sum] -> 1"))
        self.assertEquals(
            True,
            self.check_logs("Metric: 'sum.2_completed' [sum] -> 1"))
