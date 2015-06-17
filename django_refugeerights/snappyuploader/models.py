from django.db import models


class FailureLog(models.Model):
    """
    Captures the data that the user tried to upload if the upload fails.
    """
    csv_content = models.TextField(verbose_name=u'Failed upload content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"Failure to upload at %s" % (self.created_at)


class SnappyFaq(models.Model):
    """
    Stores the FAQs that are available on snappy locally.
    """
    snappy_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s" % (self.name)
