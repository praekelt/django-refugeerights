# metric = "stores.refugeerights_qa.total.ussd.sessions.transient.sum"
from datetime import datetime
from pytz import utc
from celery import task
from django.conf import settings
from go_http.metrics import MetricsApiClient
from .models import Metric, MetricRecord


def get_date():
    now = datetime.now(utc)
    # use the same time for all metrics
    date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return date


@task()
def record_all_metrics():
    """
    Task to record all metricstore values at a point in time
    """
    metrics = Metric.objects.all()
    num_metrics = 0

    for metric in metrics:
        num_metrics += 1
        fetch_metric.delay(metric)
    return "Recorded values for %d metrics" % num_metrics


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

    if len(response) > 0:
        metric_value = float(response.values()[0][-1]['y'])
        date_fetched = get_date()
        record_metric.delay(metric, date_fetched, metric_value)
        return "Fetched metric value for %s" % metric.display_name
    else:
        return "No values found for metric %s" % metric.display_name


@task()
def record_metric(metric, date_fetched, metric_value):
    """
    Records a metric at a point in time
    """
    new_metric = MetricRecord.objects.create(metric=metric,
                                             date_recorded=date_fetched,
                                             value=metric_value)
    return "Created new metric record <%s>" % new_metric.id
