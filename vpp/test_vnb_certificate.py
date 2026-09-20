"""
vpp/test_vnb_certificate.py

Unit-Tests für den 1-Klick § 14a EnWG VNB-Konformitäts-Zertifikats-Generator (PDF)
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from devices.models import Home, Device, DeviceRole, DeviceConfig
from energy.models import SteuVEDeviceConfig
from vpp.services_vnb_certificate import generate_vnb_14a_certificate_pdf

User = get_user_model()


class VNB14aCertificateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="vnb_tester",
            email="vnb_audit@sharegy.cloud",
            password="password123",
            first_name="Dr. Martin",
            last_name="Netzexperte",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Smart Prosumer Home",
            postal_code="80331",
            city="München",
        )
        self.role_consumer, _ = DeviceRole.objects.get_or_create(key="consumer", defaults={"label": "Verbraucher"})
        self.dev_wb = Device.objects.create(
            home=self.home,
            identifier="WB-14A-MUNICH-01",
            active=True,
            configured=True,
        )
        DeviceConfig.objects.create(
            device=self.dev_wb,
            home=self.home,
            role=self.role_consumer,
            name="ABL eM4 22kW Wallbox",
        )
        self.steuve = SteuVEDeviceConfig.objects.create(
            device=self.dev_wb,
            steuve_type="wallbox",
            rated_power_kw=Decimal("22.00"),
            minimum_power_kw=Decimal("4.20"),
            is_dimmable=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_generate_pdf_service_function(self):
        pdf_bytes, cert_num = generate_vnb_14a_certificate_pdf(
            device=self.dev_wb,
            user=self.user,
            malo_id="DE0001234567890123456789012345678",
            vnb_name="Bayernwerk Netz GmbH",
            steuve_types="1x ABL Wallbox (22 kW) · 1x Viessmann Wärmepumpe",
            max_power_kw="22.00",
            dimmed_limit_kw="4.20",
            reaction_time_sec="1.38",
        )

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 3000)
        self.assertTrue(cert_num.startswith("VNB-14A-"))
        # PDF Header Signature %PDF
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_vnb_certificate_pdf_rest_endpoint(self):
        resp = self.client.get(f"/api/vpp/steuve/certificate/{self.dev_wb.id}/pdf/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertIn("14a_EnWG_VNB_Konformitaets_Zertifikat_", resp["Content-Disposition"])
        self.assertTrue(resp.content.startswith(b"%PDF"))

    def test_vnb_certificate_metadata_endpoint(self):
        resp = self.client.get("/api/vpp/steuve/certificate/status/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "compliant")
        self.assertTrue(data["compliant_14a"])
        self.assertEqual(data["minimum_guaranteed_power_kw"], 4.2)
        self.assertIn("download_url", data)
