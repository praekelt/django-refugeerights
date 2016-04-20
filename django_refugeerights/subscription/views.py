from subscription.models import Subscription
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from subscription.serializers import SubscriptionSerializer
from rest_framework.exceptions import ValidationError
from contentstore.models import MessageSet
from django.http import HttpResponse


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
            messageset = MessageSet.objects.filter(pk=messageset_id).exists()
        except KeyError:
            raise ValidationError("A messageset 'id' doesn't exist")
        try:
            subscription = Subscription.objects.filter(pk=contact_key).update(active=False)
        except KeyError:
            raise ValidationError("")
