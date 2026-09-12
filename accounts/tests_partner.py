from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import Tenant
from devices.models import Home, Device
from devices.models_ocpp import ChargingStation
from accounts.models import PartnerCompany, PartnerMembership, MaintenanceConsent

User = get_user_model()


class PartnerFleetApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.partner_user = User.objects.create_user(
            username="meister@elektro-profi.de",
            email="meister@elektro-profi.de",
            password="testpassword123"
        )
        self.company = PartnerCompany.objects.create(
            name="Elektro Profi Meisterbetrieb",
            slug="elektro-profi",
            contact_email="meister@elektro-profi.de",
            partner_tier="premium"
        )
        self.membership = PartnerMembership.objects.create(
            user=self.partner_user,
            partner_company=self.company,
            role="admin"
        )

        self.customer = User.objects.create_user(
            username="kunde@web.de",
            email="kunde@web.de",
            password="password123"
        )
        self.home = Home.objects.create(
            user=self.customer,
            name="Musterhaus Schmidt",
            city="Berlin"
        )
        self.inverter = Device.objects.create(
            home=self.home,
            identifier="SUNGROW-SH10RT-01",
            active=True
        )
        self.station = ChargingStation.objects.create(
            home=self.home,
            name="Easee Home Schmidt",
            charge_point_id="CP-PARTNER-01",
            status="Available",
            is_online=True
        )
        self.consent = MaintenanceConsent.objects.create(
            home=self.home,
            partner_company=self.company,
            status="active",
            allow_remote_control=True
        )

        self.client.force_authenticate(user=self.partner_user)

    def test_partner_fleet_view(self):
        res = self.client.get("/api/partner/fleet/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["partner_company"]["name"], "Elektro Profi Meisterbetrieb")
        self.assertEqual(res.data["summary"]["total_homes"], 1)

    def test_partner_quick_onboard(self):
        payload = {
            "customer_email": "neukunde@haus.de",
            "home_name": "Neubau Müller",
            "city": "Köln",
            "street": "Sonnenweg 5"
        }
        res = self.client.post("/api/partner/quick-onboard/", data=payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data["success"])
        self.assertTrue(MaintenanceConsent.objects.filter(partner_company=self.company, home__user__email="neukunde@haus.de").exists())

    def test_partner_diagnostics(self):
        res = self.client.post(f"/api/partner/diagnostics/{self.station.id}/", data={"action": "ping"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["success"])
        self.assertEqual(res.data["asset_type"], "wallbox")
