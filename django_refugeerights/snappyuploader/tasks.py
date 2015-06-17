from __future__ import absolute_import

from celery.task import Task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

from django.conf import settings


logger = get_task_logger(__name__)


class CSV_Importer(Task):

    """
    Task to take dict import the data
    """
    name = "snappyuploader.tasks.csv_importer"

    class FailedEventRequest(Exception):

        """
        The attempted task failed because of a non-200 HTTP return
        code.
        """

    def run(self, csv_data, faq_id, **kwargs):
        """
        Returns count of imported faqs
        """
        l = self.get_logger(**kwargs)

        l.info("Processing new snappy FAQ import data")
        imported = 0
        row = 0
        try:
            # for line in poidata:
            #     row += 1
            #     if "Latitude" in line and "Longitude" in line:
            #         if line["Longitude"] != "" and line["Latitude"] != "":
            #             poi_point = Point(float(line["Longitude"]),
            #                               float(line["Latitude"]))
            #             # check if point exists
            #             locations = Location.objects.filter(point=poi_point)
            #             if locations.count() == 0:
            #                 # make a Location
            #                 location = Location()
            #                 location.point = poi_point
            #                 location.save()
            #             else:
            #                 # Grab the top of the stack
            #                 location = locations[0]
            #             # Create new point of interest with location
            #             poi = PointOfInterest()
            #             poi.location = location
            #             poi.data = line
            #             poi.save()
            #             imported += 1
            #             l.info("Imported: %s" % line["Clinic Name"])
            #         else:
            #             l.info(
            #                 "Row <%s> has corrupted point data, "
            #                 "not imported" % row)
            #     else:
            #         l.info("Row <%s> missing point data, not imported" % row)
            # l.info("Imported <%s> locations" % str(imported))
            return imported
        except SoftTimeLimitExceeded:
            logger.error(
                'Soft time limit exceed processing location import \
                 via Celery.',
                exc_info=True)

csv_importer = CSV_Importer()
