from .models import (Location, PointOfInterest,
                     LookupLocation, LookupPointOfInterest)
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework_gis.serializers import GeoModelSerializer


class LocationSerializer(GeoModelSerializer):

    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Location
        geo_field = "point"

        # you can also explicitly declare which fields you want to include
        # as with a ModelSerializer.
        fields = ('id', 'point')


class PointOfInterestSerializer(HyperlinkedModelSerializer):
    location = LocationSerializer(many=False, read_only=False)

    class Meta:
        model = PointOfInterest
        fields = ('url', 'id', 'data', 'location')

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        loc = Location.objects.create(**location_data)
        poi = PointOfInterest.objects.create(location=loc, **validated_data)
        return poi


class LookupLocationSerializer(GeoModelSerializer):

    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = LookupLocation
        geo_field = "point"

        # you can also explicitly declare which fields you want to include
        # as with a ModelSerializer.
        fields = ('id', 'point')


class LookupPointOfInterestSerializer(HyperlinkedModelSerializer):
    location = LookupLocationSerializer(many=False, read_only=False)

    class Meta:
        model = LookupPointOfInterest
        fields = (
            'url', 'search', 'response', 'location')

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        lloc = LookupLocation.objects.create(**location_data)
        lpoi = LookupPointOfInterest.objects.create(location=lloc,
                                                    **validated_data)
        return lpoi
