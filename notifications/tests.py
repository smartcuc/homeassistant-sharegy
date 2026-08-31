from django.test import TestCase
from django.contrib.auth import get_user_model
from devices.models import Home
from notifications.models import DeviceSubscription, NotificationPreference
from notifications.services import is_in_quiet_hours, send_test_push

User = get_user_model()


class NotificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="pushtest@sharegy.cloud",
            email="pushtest@sharegy.cloud",
            password="securePassword123!",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Zuhause Test",
            city="Berlin",
            postal_code="10115",
            timezone="Europe/Berlin",
        )

    def test_device_subscription_creation(self):
        sub = DeviceSubscription.objects.create(
            user=self.user,
            home=self.home,
            device_type=DeviceSubscription.DEVICE_WEB_PUSH,
            endpoint="https://fcm.googleapis.com/fcm/send/fake-endpoint-token",
            p256dh_key="fake-p256dh",
            auth_key="fake-auth",
            device_name="Safari auf iPhone 15",
        )
        self.assertTrue(sub.is_active)
        self.assertEqual(DeviceSubscription.objects.filter(user=self.user).count(), 1)

    def test_preferences_defaults(self):
        pref, created = NotificationPreference.objects.get_or_create(user=self.user)
        self.assertTrue(pref.push_enabled)
        self.assertFalse(pref.quiet_hours_enabled)
        self.assertFalse(is_in_quiet_hours(pref))

    def test_test_push_with_no_devices(self):
        res = send_test_push(self.user)
        self.assertFalse(res["success"])
        self.assertEqual(res["count"], 0)
