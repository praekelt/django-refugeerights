from subscription.models import Subscription
from rest_framework import serializers


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('url', 'id', 'contact_key', 'to_addr', 'messageset_id',
                  'next_sequence_number', 'lang', 'active', 'completed',
                  'schedule', 'process_status', 'created_at', 'updated_at')
