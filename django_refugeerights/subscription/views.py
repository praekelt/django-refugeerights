from subscription.models import Subscription
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from subscription.serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows subscription models to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
