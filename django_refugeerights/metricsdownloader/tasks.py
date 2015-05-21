# metric = "stores.refugeerights_qa.total.ussd.sessions.transient.sum"
from datetime import datetime
from celery import task
from django.conf import settings
from go_http.metrics import MetricsApiClient
from .models import Metric, MetricRecord


def get_date():
    today = datetime.today()
    # use the same time for all metrics
    date = datetime(today.year, today.month, today.day)
    return date


@task()
def record_all_metrics():
    """
    Task to record all metricstore values at a point in time
    """
    metrics = Metric.objects.all()

    for metric in metrics:
        fetch_metric.delay(metric)


@task()
def fetch_metric(metric):
    """
    Task to look up a metric value from the metricstore
    """
    metric_client = MetricsApiClient(settings.METRIC_API_KEY)
    response = metric_client.get_metric(
        metric.lookup_name,
        "-" + settings.METRIC_RECORDING_INTERVAL,
        settings.METRIC_RECORDING_INTERVAL,
        "")
    metric_value = float(response.values()[0][-1]['y'])
    date_fetched = get_date()

    record_metric.delay(metric, date_fetched, metric_value)


@task()
def record_metric(metric, date_fetched, metric_value):
    """
    Records a metric at a point in time
    """
    MetricRecord.objects.create(metric=metric, date_recorded=date_fetched,
                                value=metric_value)
