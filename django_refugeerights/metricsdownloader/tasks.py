# metric = "stores.refugeerights_qa.total.ussd.sessions.transient.sum"
from datetime import datetime
from celery import task
from django.conf import settings
from go_http.metrics import MetricsApiClient
from .models import Metric, MetricRecord


@task
def record_metric(metric):
    """
    Records a metric from the metricstore at a point in time
    """
    metric_client = MetricsApiClient(settings.METRIC_API_KEY)
    response = metric_client.get_metric(
        metric.lookup_name,
        "-" + settings.METRIC_RECORDING_INTERVAL,
        settings.METRIC_RECORDING_INTERVAL,
        "")
    metric_value = int(float(response.values()[0][-1]['y']))
    today = datetime.today()
    # use the same time for all metrics
    date_recorded = datetime(today.year, today.month, today.day)
    MetricRecord.objects.create(metric, date_recorded, metric_value)


@task()
def record_metrics():
    """
    Task to record all metricstore values at a point in time
    """
    metrics = Metric.objects.all()

    for metric in metrics:
        record_metric(metric)
