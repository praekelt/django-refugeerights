from django.db import models as djangomodels
from django.contrib.gis.db import models as gismodels
from django_hstore import hstore
from django.db.models.signals import post_save
from django.dispatch import receiver


class HStoreModel(djangomodels.Model):
    objects = hstore.HStoreManager()

    class Meta:
        abstract = True


class Location(gismodels.Model):
    point = gismodels.PointField()
    created_at = djangomodels.DateTimeField(auto_now_add=True)
    updated_at = djangomodels.DateTimeField(auto_now=True)

    # GeoDjango-specific overriding the default manager with a
    # GeoManager instance.
    objects = gismodels.GeoManager()

    def __unicode__(self):
        return u"%s" % (self.point)


class PointOfInterest(HStoreModel):

    """
    Extendable point of interest model
    """
    created_at = djangomodels.DateTimeField(auto_now_add=True)
    updated_at = djangomodels.DateTimeField(auto_now=True)
    # can pass attributes like null, blank, etc.
    data = hstore.DictionaryField()
    location = djangomodels.ForeignKey(Location, related_name='location')

    def __unicode__(self):
        # This will only work while the data is well structured
        if "Location Name" in self.data:
            return u"%s at %s, %s" % (self.data["Location Name"],
                                      self.location.point.x,
                                      self.location.point.y)
        else:
            return u"Point of Interest at %s, %s" % \
                (self.location.point.x, self.location.point.y)


class LookupLocation(gismodels.Model):

    """
    Inbound lookups are stored here and trigger
    """
    point = gismodels.PointField()

    created_at = djangomodels.DateTimeField(auto_now_add=True)
    updated_at = djangomodels.DateTimeField(auto_now=True)

    # GeoDjango-specific overriding the default manager with a
    # GeoManager instance.
    objects = gismodels.GeoManager()

    def __unicode__(self):
        return u"%s" % (self.point)


class LookupPointOfInterest(HStoreModel):

    """
    Extendable point of interest request model
    """
    created_at = djangomodels.DateTimeField(auto_now_add=True)
    updated_at = djangomodels.DateTimeField(auto_now=True)
    # can pass attributes like null, blank, etc.
    search = hstore.DictionaryField()
    response = hstore.DictionaryField()
    location = djangomodels.ForeignKey(
        LookupLocation, related_name='lookup_location',
        blank=True, null=True)

    def __unicode__(self):
        # This will only work while the data is well structured
        if "to_addr" in self.response and self.location is not None:
            return u"%s at %s, %s" % (self.response["to_addr"],
                                      self.location.point.x,
                                      self.location.point.y)
        elif self.location is not None:
            return u"Lookup at %s, %s" % (self.location.point.x,
                                          self.location.point.y)
        else:
            return u"Lookup timed at %s" % (self.created_at)

# Tasks import models from this file so must go here
from .tasks import location_finder


@receiver(post_save, sender=LookupPointOfInterest)
def fire_location_finder_task_if_complete(sender, instance, created, **kwargs):
    # Lookup locaction in place and results not in place already
    if instance.location is not None and "results" not in instance.response:
        # find match and prepare response
        location_finder.delay(instance.id)
