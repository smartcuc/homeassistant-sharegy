###################
# alerts/tests.py
###################

from django.test import TestCase
from django.contrib.auth import get_user_model
from devices.models import Home, Device, DeviceRole, DeviceConfig, DeviceLatestMetric
from alerts.models import AlertEvent
from alerts.services import evaluate_home_alerts

User = get_user_model()


class AlertsEngineTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alerttestuser",
            email="alerts@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Alert Test Home",
            latitude=50.9375,
            longitude=6.9603,
        )

    def test_battery_empty_alert_generation(self):
        role_bat = DeviceRole.objects.create(key="battery", label="Hausspeicher")
        bat_dev = Device.objects.create(home=self.home, identifier="bat_test_01", configured=True)
        DeviceConfig.objects.create(device=bat_dev, home=self.home, role=role_bat)

        DeviceLatestMetric.objects.create(
            device=bat_dev,
            metric_key="soc",
            value=6.5,  # Unter 10%
            timestamp="2026-08-25T02:00:00Z",
        )

        active_alerts = evaluate_home_alerts(self.home)
        self.assertGreaterEqual(len(active_alerts), 1)

        bat_alert = next((a for a in active_alerts if a.alert_type == "battery_empty"), None)
        self.assertIsNotNone(bat_alert)
        self.assertEqual(bat_alert.severity, AlertEvent.SEVERITY_CRITICAL)

    def test_alerts_api_list_and_acknowledge(self):
        from billing.models import EMSSubscription
        sub = EMSSubscription.objects.filter(user=self.user).first()
        if sub:
            sub.plan = "pro_monthly"
            sub.status = "active"
            sub.save()
        else:
            EMSSubscription.objects.create(user=self.user, plan="pro_monthly", status="active")

        # 1. Erstelle Batterie-Gerät mit niedrigem SoC
        role_bat, _ = DeviceRole.objects.get_or_create(key="battery", defaults={"label": "Hausspeicher"})
        bat_dev = Device.objects.create(home=self.home, identifier="bat_test_ack", configured=True)
        DeviceConfig.objects.create(device=bat_dev, home=self.home, role=role_bat)
        DeviceLatestMetric.objects.create(
            device=bat_dev,
            metric_key="soc",
            value=7.0,
            timestamp="2026-08-25T02:00:00Z",
        )

        # 2. Get alerts list
        self.client.force_login(self.user)
        list_resp = self.client.get("/api/alerts/")
        self.assertEqual(list_resp.status_code, 200)
        data = list_resp.json()

        self.assertIn("summary", data)
        self.assertIn("alerts", data)
        self.assertGreaterEqual(len(data["alerts"]), 1)

        alert_id = data["alerts"][0]["id"]

        # 3. Acknowledge alert
        ack_resp = self.client.post(f"/api/alerts/{alert_id}/acknowledge/")
        self.assertEqual(ack_resp.status_code, 200)
        self.assertEqual(ack_resp.json()["status"], "acknowledged")

        # 4. Resolve alert
        res_resp = self.client.post(f"/api/alerts/{alert_id}/resolve/")
        self.assertEqual(res_resp.status_code, 200)
        self.assertEqual(res_resp.json()["status"], "resolved")

    def test_alerts_free_user_gating(self):
        # Free User must get pro_required: True and empty alerts
        self.client.force_login(self.user)
        list_resp = self.client.get("/api/alerts/")
        self.assertEqual(list_resp.status_code, 200)
        data = list_resp.json()
        self.assertFalse(data.get("is_pro"))
        self.assertTrue(data.get("pro_required"))

    def test_negative_pv_generation_does_not_trigger_no_pv_alert(self):
        role_pv = DeviceRole.objects.create(key="producer", label="PV Wechselrichter")
        pv_dev = Device.objects.create(home=self.home, identifier="pv_inverter_01", configured=True)
        DeviceConfig.objects.create(device=pv_dev, home=self.home, role=role_pv)

        # Wechselrichter meldet Einspeisung als negativen Wert (-1074 W)
        DeviceLatestMetric.objects.create(
            device=pv_dev,
            metric_key="power",
            value=-1074.0,
            timestamp="2026-08-25T15:00:00Z",
        )

        active_alerts = evaluate_home_alerts(self.home)
        no_pv_alert = next((a for a in active_alerts if a.alert_type == "no_pv"), None)
        self.assertIsNone(no_pv_alert, "Negative PV-Leistung (-1074 W Einspeisung) darf keinen Ertragsausfall-Alarm auslösen")

