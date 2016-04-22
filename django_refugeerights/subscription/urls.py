from django.conf.urls import url, include
from rest_framework import routers
import views

router = routers.DefaultRouter()
router.register(r'subscription', views.SubscriptionViewSet)
router.register(r'switch_subscription', views.SwitchSubscriptionView, base_name="SwitchSubscription")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^', include(router.urls)),
]
