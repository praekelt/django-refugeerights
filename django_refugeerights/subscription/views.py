from subscription.models import Subscription
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from subscription.serializers import SubscriptionSerializer
from rest_framework.exceptions import ValidationError
from contentstore.models import MessageSet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djcelery.models import PeriodicTask


class SubscriptionViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows subscription models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    filter_fields = ('contact_key', 'to_addr', 'active', )


class SwitchSubscriptionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        data = request.data
        try:
            contact_key = data['contact_key']
        except KeyError:
            raise ValidationError("A contact 'key' parameter is required.")
        try:
            messageset_id = data['messageset_id']
        except KeyError:
            raise ValidationError("A messageset 'id' parameter is required.")

        try:
            schedule_id = data['schedule']
        except KeyError:
            raise ValidationError(
                "A messageset 'schedule' parameter is required.")

        messageset_exists = MessageSet.objects.filter(
            pk=messageset_id).exists()
        if not messageset_exists:
            raise ValidationError("A messageset 'id' doesn't exist")

        schedule = get_object_or_404(PeriodicTask, id=int(schedule_id))

        Subscription.objects.filter(
            contact_key=contact_key,
            active=True, completed=False).update(active=False)

        Subscription.objects.create(messageset_id=messageset_id,
                                    contact_key=contact_key,
                                    schedule=schedule)
        return HttpResponse(status=200)
