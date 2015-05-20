from django.db import models


class Metric(models.Model):
    lookup_name = models.CharField(max_length=255, null=False, blank=False)
    display_name = models.CharField(max_length=25, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Metric %s" % (self.display_name)


class MetricRecord(models.Model):
    metric = models.ForeignKey(Metric, related_name='metric', null=False)
    date_recorded = models.DateTimeField(null=False, blank=False)
    value = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s as on %s" % (self.metric, self.date_recorded)
