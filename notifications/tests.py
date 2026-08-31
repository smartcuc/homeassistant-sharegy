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
        from billing.models import EMSSubscription
        EMSSubscription.objects.update_or_create(user=self.user, defaults={"plan": "pro_monthly", "status": "active"})

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

    def test_subscribe_and_unsubscribe_audit_ip(self):
        from django.test import Client
        client = Client()
        client.force_login(self.user)

        # 1. Subscribe Device
        res_sub = client.post(
            "/api/notifications/subscribe/",
            data={
                "endpoint": "https://push.example.com/sub/123",
                "keys": {"p256dh": "key1", "auth": "key2"},
                "device_name": "Pixel 8 Pro",
            },
            content_type="application/json",
            REMOTE_ADDR="198.51.100.42",
        )
        self.assertEqual(res_sub.status_code, 200)
        sub = DeviceSubscription.objects.get(endpoint="https://push.example.com/sub/123")
        self.assertTrue(sub.is_active)
        self.assertEqual(sub.registered_ip, "198.51.100.42")
        self.assertIsNone(sub.unregistered_at)

        # 2. Preferences listing devices
        res_pref = client.get("/api/notifications/preferences/", REMOTE_ADDR="198.51.100.42")
        self.assertEqual(res_pref.status_code, 200)
        self.assertEqual(res_pref.json()["active_devices_count"], 1)
        self.assertEqual(len(res_pref.json()["devices"]), 1)
        self.assertEqual(res_pref.json()["devices"][0]["registered_ip"], "198.51.100.42")

        # 3. Unsubscribe Device by Endpoint
        res_unsub = client.post(
            "/api/notifications/unsubscribe/",
            data={"endpoint": "https://push.example.com/sub/123"},
            content_type="application/json",
            REMOTE_ADDR="198.51.100.99",
        )
        self.assertEqual(res_unsub.status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)
        self.assertEqual(sub.unregistered_ip, "198.51.100.99")
        self.assertIsNotNone(sub.unregistered_at)

        # 4. Delete / Unsubscribe by ID
        sub.is_active = True
        sub.save()
        res_del = client.post(
            f"/api/notifications/devices/{sub.id}/delete/",
            REMOTE_ADDR="203.0.113.10",
        )
        self.assertEqual(res_del.status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)
        self.assertEqual(sub.unregistered_ip, "203.0.113.10")
