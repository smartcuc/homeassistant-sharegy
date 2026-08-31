############################
# notifications/api/urls.py
############################

from django.urls import path
from notifications.api import views

urlpatterns = [
    path("vapid-key/", views.vapid_public_key, name="notifications_vapid_key"),
    path("subscribe/", views.subscribe_device, name="notifications_subscribe"),
    path("unsubscribe/", views.unsubscribe_device, name="notifications_unsubscribe"),
    path("preferences/", views.notification_preferences, name="notifications_preferences"),
    path("test-push/", views.trigger_test_push, name="notifications_test_push"),
]
