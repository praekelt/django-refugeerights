from django.contrib.auth.models import User
from django.test import TestCase
from .models import Metric, MetricRecord
from .tasks import record_metric, get_date


class MetricsRecordingTest(TestCase):

    fixtures = ["test_metrics.json"]

    def setUp(self):
        super(MetricsRecordingTest, self).setUp()

        # Create a user.
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(self.username,
                                             'testuser@example.com',
                                             self.password)

    def test_data_loaded(self):
        users = User.objects.all()
        self.assertEqual(users.count(), 1)
        metrics = Metric.objects.all()
        self.assertEqual(metrics.count(), 2)
        metricrecords = MetricRecord.objects.all()
        self.assertEqual(metricrecords.count(), 2)

    def test_record_metrics(self):
        metric = Metric.objects.all()[0]
        date_fetched = get_date()
        metric_value = 55.7
        record_metric.delay(metric, date_fetched, metric_value)

        metricrecords = MetricRecord.objects.all()
        self.assertEqual(metricrecords.count(), 3)
        added_metricrecord = MetricRecord.objects.all()[2]
        self.assertEqual(added_metricrecord.value, 55.7)
