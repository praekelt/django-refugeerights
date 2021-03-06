from django.db import models


class Metric(models.Model):
    lookup_name = models.CharField(max_length=255, null=False, blank=False)
    display_name = models.CharField(max_length=50, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"Metric %s" % (self.display_name)


class MetricRecord(models.Model):
    metric = models.ForeignKey(Metric, related_name='records', null=False)
    date_recorded = models.DateTimeField(null=False, blank=False)
    value = models.FloatField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s as on %s" % (self.metric, self.date_recorded)
