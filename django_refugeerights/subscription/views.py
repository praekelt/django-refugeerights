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

        messageset_exists = MessageSet.objects.filter(
            pk=messageset_id).exists()
        if not messageset_exists:
            raise ValidationError("A messageset 'id' doesn't exist")

        Subscription.objects.filter(
            pk=contact_key, active=True, completed=False).update(active=False)
        Subscription.create(messageset_id=messageset_id,
                          messageset_exists=messageset_exists)
        return HttpResponse(status=200)
