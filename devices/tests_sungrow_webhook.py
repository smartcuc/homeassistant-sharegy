import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

from devices.models import Home, Device, CloudDeviceIntegration
from energy.services.system_health import check_home_system_status

User = get_user_model()

class SungrowWebhookTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.user = User.objects.create_user(username="sungrow_user", email="user@sharegy.de", password="pw")
        self.home = Home.objects.create(user=self.user, name="Musterhaus")
        self.device = Device.objects.create(
            home=self.home,
            identifier="SUNGROW-SH10RT-12345",
            active=True,
        )
        self.integration = CloudDeviceIntegration.objects.create(
            device=self.device,
            profile_id="sungrow_isolarcloud",
            credentials={"ps_id": "999888"},
            is_active=True,
        )

    def test_get_challenge_handshake(self):
        res = self.client.get("/api/integrations/webhooks/sungrow/?echostr=test_challenge_123")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content.decode("utf-8"), "test_challenge_123")

    def test_post_challenge_handshake(self):
        res = self.client.post(
            "/api/integrations/webhooks/sungrow/",
            data=json.dumps({"echostr": "post_echo_999"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"echostr": "post_echo_999"})

    def test_alarm_event_and_recovery(self):
        # 1. Alarm senden: Grid Under-Voltage (Code 102)
        alarm_payload = {
            "ps_id": "999888",
            "fault_code": 102,
            "fault_name": "Grid Under-Voltage",
            "fault_level": "alarm",
            "status": 1,
        }
        res = self.client.post(
            "/api/integrations/webhooks/sungrow/",
            data=json.dumps(alarm_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["is_recovered"])

        # System Health prüfen: Alarm muss erkannt sein
        status = check_home_system_status(self.user)
        self.assertEqual(status["status"], "fault")
        self.assertEqual(len(status["alarms"]), 1)
        self.assertEqual(status["alarms"][0]["code"], 102)

        # 2. Entwarnung / Recovery senden: Code 102 behoben
        recovery_payload = {
            "ps_id": "999888",
            "fault_code": 102,
            "fault_name": "Grid Under-Voltage Recovered",
            "status": 2,
        }
        res_rec = self.client.post(
            "/api/integrations/webhooks/sungrow/",
            data=json.dumps(recovery_payload),
            content_type="application/json"
        )
        self.assertEqual(res_rec.status_code, 200)
        self.assertTrue(res_rec.json()["is_recovered"])

        # System Health prüfen: Alarm muss gelöscht sein
        status_after = check_home_system_status(self.user)
        self.assertEqual(len(status_after["alarms"]), 0)
