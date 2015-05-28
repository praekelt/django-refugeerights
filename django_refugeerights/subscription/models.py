from django.db import models
from djcelery.models import PeriodicTask


class Subscription(models.Model):

    """
    Users subscriptions and their status
    """
    contact_key = models.CharField(max_length=36, null=False, blank=False)
    to_addr = models.CharField(max_length=255, null=False, blank=False)
    messageset_id = models.IntegerField(null=False, blank=False)
    next_sequence_number = models.IntegerField(default=1, null=False,
                                               blank=False)
    lang = models.CharField(max_length=6, null=False, blank=False)
    active = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)
    schedule = models.ForeignKey(PeriodicTask,
                                 related_name='subscriptions',
                                 null=False)
    process_status = models.IntegerField(default=0, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s to message set %d" % (self.contact_key, self.messageset_id)
