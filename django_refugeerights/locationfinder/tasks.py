from __future__ import absolute_import

from celery.task import Task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from go_http.send import HttpApiSender

from django.conf import settings

from .models import (LookupPointOfInterest, PointOfInterest, Location)

logger = get_task_logger(__name__)


class Metric_Sender(Task):

    """
    Task to fire metrics at Vumi
    """
    name = "clinicfinder.tasks.metric_sender"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return
        code.
        """

    def vumi_client(self):
        return HttpApiSender(
            account_key=settings.VUMI_GO_ACCOUNT_KEY,
            conversation_key=settings.VUMI_GO_CONVERSATION_KEY,
            conversation_token=settings.VUMI_GO_ACCOUNT_TOKEN
        )

    def run(self, metric, value, agg, **kwargs):
        """
        Returns count of imported records
        """
        l = self.get_logger(**kwargs)

        l.info("Firing metric: %r [%s] -> %g" % (metric, agg, float(value)))
        try:
            sender = self.vumi_client()
            result = sender.fire_metric(metric, value, agg=agg)
            l.info("Result of firing metric: %s" % (result["success"]))
            return result

        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing metric fire \
                 via Celery.',
                exc_info=True)

metric_sender = Metric_Sender()


class Location_Finder(Task):

    """
    Task to take location and search for results
    """
    name = "clinicfinder.tasks.location_finder"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return
        code.
        """

    def format_match(self, match):
        primary = "Location Name"
        additional = ["Street Address", "Primary Contact Number"]
        add_output = ', '.join(
            match.data[key] for key in additional
            if key in match.data and match.data[key] != "")
        formatted = "%s (%s)" % (match.data[primary], add_output)
        return (match.id, formatted)

    def run(self, lookuppointofinterest_id, **kwargs):
        """
        Returns a filtered list of locations for query
        """
        l = self.get_logger(**kwargs)

        l.info("Processing new location search")
        try:

            ringfence = Distance(km=settings.LOCATION_SEARCH_RADIUS)
            lookuppoi = LookupPointOfInterest.objects.get(
                pk=lookuppointofinterest_id)
            locations = Location.objects.filter(
                point__distance_lte=(
                    lookuppoi.location.point, ringfence)).filter(
                location__data__contains=lookuppoi.search).distance(
                lookuppoi.location.point).order_by('distance')
            matches = []
            for result in locations:
                for poi in result.location.all():
                    matches.append(poi)

            submission = matches[:settings.LOCATION_MAX_RESPONSES]
            total = len(submission)
            if total != 0:
                formatted = [self.format_match(match) for match in submission]
                output = ' AND '.join(match[1] for match in formatted)
            else:
                output = ""
                formatted = []
            lookuppoi.response["results"] = output
            lookuppoi.response["results_detailed"] = formatted
            lookuppoi.save()
            l.info("Completed location search. Found: %s" % str(total))
            return True
        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing location search \
                 via Celery.',
                exc_info=True)

location_finder = Location_Finder()


class PointOfInterest_Importer(Task):

    """
    Task to take dict import the data
    """
    name = "clinicfinder.tasks.pointofinterest_importer"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return
        code.
        """

    def run(self, poidata, **kwargs):
        """
        Returns count of imported records
        """
        l = self.get_logger(**kwargs)

        l.info("Processing new point of interest import data")
        imported = 0
        row = 0
        try:
            for line in poidata:
                row += 1
                if "Latitude" in line and "Longitude" in line:
                    if line["Longitude"] != "" and line["Latitude"] != "":
                        poi_point = Point(float(line["Longitude"]),
                                          float(line["Latitude"]))
                        # check if point exists
                        locations = Location.objects.filter(point=poi_point)
                        if locations.count() == 0:
                            # make a Location
                            location = Location()
                            location.point = poi_point
                            location.save()
                        else:
                            # Grab the top of the stack
                            location = locations[0]
                        # Create new point of interest with location
                        poi = PointOfInterest()
                        poi.location = location
                        poi.data = line
                        poi.save()
                        imported += 1
                        l.info("Imported: %s" % line["Location Name"])
                    else:
                        l.info(
                            "Row <%s> has corrupted point data, "
                            "not imported" % row)
                else:
                    l.info("Row <%s> missing point data, not imported" % row)
            l.info("Imported <%s> locations" % str(imported))
            return imported
        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing location import \
                 via Celery.',
                exc_info=True)

pointofinterest_importer = PointOfInterest_Importer()
