#######################################
# devices/tests_shelly_cloud.py
#######################################

from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from devices.models import Home, Device, DeviceConfig
from devices.services_shelly_cloud import ShellyCloudService

User = get_user_model()


class ShellyCloudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="shellyuser",
            email="shelly@example.com",
            password="securepassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Zuhause Test",
            city="Berlin",
            postal_code="10115",
            mqtt_token="HOMETESTTOKEN123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("requests.post")
    def test_shelly_cloud_test_connection_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "isok": True,
            "data": {
                "devices": {
                    "e8db84d12345": {
                        "name": "Hauptzähler Pro 3EM",
                        "code": "shellypro3em",
                        "online": True,
                        "status": {"apower": 1450.0},
                    },
                    "c45bbe998877": {
                        "name": "Balkonkraftwerk PM",
                        "code": "shellyplus1pm",
                        "online": True,
                        "status": {"apower": 580.0},
                    },
                }
            },
        }
        mock_post.return_value = mock_resp

        res = ShellyCloudService.test_connection(auth_key="test_auth_key", server_url="https://shelly-45-eu.shelly.cloud")
        self.assertTrue(res["success"])
        self.assertEqual(res["device_count"], 2)
        self.assertEqual(len(res["devices"]), 2)

    @patch("requests.post")
    def test_shelly_cloud_import_all_devices(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "isok": True,
            "data": {
                "devices": {
                    "e8db84d12345": {
                        "name": "Hauptzähler Pro 3EM",
                        "code": "shellypro3em",
                        "online": True,
                        "status": {"emeters": [{"power": 2300.0}]},
                    },
                    "c45bbe998877": {
                        "name": "Balkonkraftwerk PM",
                        "code": "shellyplus1pm",
                        "online": True,
                        "status": {"apower": 650.0},
                    },
                }
            },
        }
        mock_post.return_value = mock_resp

        res = ShellyCloudService.import_all_devices(
            home=self.home,
            auth_key="test_auth_key",
            server_url="https://shelly-45-eu.shelly.cloud",
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["created_count"], 2)

        # Überprüfen, ob Geräte in der DB existieren
        from devices.models import CloudDeviceIntegration
        meter = Device.objects.get(identifier="shelly-e8db84d12345")
        self.assertEqual(meter.config.name, "Hauptzähler Pro 3EM")
        self.assertTrue(meter.active)
        self.assertTrue(meter.configured)

        plug = Device.objects.get(identifier="shelly-c45bbe998877")
        self.assertEqual(plug.config.name, "Balkonkraftwerk PM")

        # Configs prüfen
        integration = CloudDeviceIntegration.objects.get(device=meter)
        self.assertEqual(integration.credentials["auth_key"], "test_auth_key")

    @patch("requests.post")
    def test_shelly_cloud_api_endpoints(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "isok": True,
            "data": {
                "devices": {
                    "aabbcc112233": {
                        "name": "Wärmepumpe Shelly",
                        "code": "shellyplus1pm",
                        "online": True,
                        "status": {"apower": 1200.0},
                    }
                }
            },
        }
        mock_post.return_value = mock_resp

        # Test Discovery API
        test_url = "/api/devices/shelly-cloud/test/"
        resp = self.client.post(test_url, {"auth_key": "dummy_key"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["success"])

        # Import API
        import_url = "/api/devices/shelly-cloud/import/"
        resp = self.client.post(
            import_url,
            {"auth_key": "dummy_key", "home_id": self.home.id},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["created_count"], 1)
