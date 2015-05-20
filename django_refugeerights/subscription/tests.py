import json
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


from subscription.models import Subscription
from djcelery.models import PeriodicTask
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


class TestSubsription(AuthenticatedAPITestCase):

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
        self.assertEqual(d.schedule.id, 1)
