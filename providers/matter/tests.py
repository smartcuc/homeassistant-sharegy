from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from devices.models import Home, Device, DeviceLatestMetric, DeviceMetric1h
from providers.matter.models import MatterFabric, MatterNode, MatterCluster, MatterEndpoint
from providers.matter.services.commissioning import (
    parse_matter_pairing_code,
    commission_matter_node,
)
from providers.matter.services.cluster_engine import (
    process_matter_attribute_report,
    execute_matter_command,
    simulate_matter_telemetry,
)

User = get_user_model()


class MatterHubAndClusterTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="matteruser",
            email="matter@sharegy.cloud",
            password="matterpass123!",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Matter Test Home",
            mqtt_token="MATTERTESTTOKEN",
            mqtt_password="MATTERTESTPASS123",
        )
        self.client.force_authenticate(user=self.user)

    def test_parse_matter_pairing_code(self):
        # 1. QR Code
        qr_parsed = parse_matter_pairing_code("MT:Y.K9042C00KA0648G00")
        self.assertEqual(qr_parsed["type"], "qr_code")
        self.assertIn("discriminator", qr_parsed)
        self.assertIn("setup_pin", qr_parsed)

        # 2. 11-digit manual code
        man11_parsed = parse_matter_pairing_code("34970112332")
        self.assertEqual(man11_parsed["type"], "manual_11")
        self.assertEqual(man11_parsed["setup_pin"], "970112332")

        # 3. 21-digit manual code
        man21_parsed = parse_matter_pairing_code("349701123329988776655")
        self.assertEqual(man21_parsed["type"], "manual_21")

    def test_commission_matter_smart_plug(self):
        node = commission_matter_node(
            home=self.home,
            name="Eve Energy Matter Plug",
            pairing_code="MT:Y.K9042C00KA0648G00",
            device_type="smart_plug",
            custom_role="consumer",
        )

        self.assertIsNotNone(node.id)
        self.assertEqual(node.name, "Eve Energy Matter Plug")
        self.assertEqual(node.device_type, "smart_plug")
        self.assertIsNotNone(node.device)
        self.assertEqual(node.device.config.name, "Eve Energy Matter Plug")
        self.assertEqual(node.device.config.role.key, "consumer")

        # Prüfe Endpoints & Clusters
        endpoints = node.endpoints.all()
        self.assertEqual(endpoints.count(), 1)
        clusters = endpoints.first().clusters.all()
        cluster_ids = [c.cluster_id for c in clusters]
        self.assertIn(0x0006, cluster_ids) # On/Off
        self.assertIn(0x0090, cluster_ids) # Power Measurement
        self.assertIn(0x0091, cluster_ids) # Energy Measurement

    def test_matter_cluster_attribute_processing(self):
        node = commission_matter_node(
            home=self.home,
            name="Matter EVSE Wallbox",
            pairing_code="34970112332",
            device_type="evse",
        )

        # Simuliere Bericht von Cluster 0x0090 (Power) und 0x0091 (Energy)
        res = process_matter_attribute_report(
            node=node,
            endpoint_id=1,
            cluster_id=0x0090,
            attributes={
                "active_power_w": 11000.0,
                "rms_voltage_mv": 230000,
                "active_current_ma": 16000,
            },
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["power_w"], 11000.0)

        # Prüfe, ob DeviceLatestMetric und DeviceMetric1h angelegt wurden
        latest_metric = DeviceLatestMetric.objects.filter(
            device=node.device, metric_key="power"
        ).first()
        self.assertIsNotNone(latest_metric)
        self.assertEqual(latest_metric.value, 11000.0)

        hourly_metric = DeviceMetric1h.objects.filter(
            device=node.device, metric_key="power"
        ).first()
        self.assertIsNotNone(hourly_metric)
        self.assertEqual(hourly_metric.avg, 11000.0)

    def test_matter_commands(self):
        node = commission_matter_node(
            home=self.home,
            name="Küche Kaffeemaschine Plug",
            pairing_code="20202021",
            device_type="smart_plug",
        )

        # Toggle Command
        res_toggle = execute_matter_command(node, "toggle")
        self.assertEqual(res_toggle["status"], "success")
        node.refresh_from_db()
        self.assertFalse(node.attributes_payload["on_off"])

        # Turn on
        res_on = execute_matter_command(node, "turn_on")
        self.assertEqual(res_on["status"], "success")
        node.refresh_from_db()
        self.assertTrue(node.attributes_payload["on_off"])

    def test_matter_api_endpoints(self):
        # 1. Commissioning API
        res_comm = self.client.post(
            "/api/matter/commission/",
            {
                "name": "Wärmepumpe Matter",
                "pairing_code": "MT:Y.K9042C00KA0648G00",
                "device_type": "heatpump",
                "role": "consumer",
            },
            format="json",
        )
        self.assertEqual(res_comm.status_code, status.HTTP_201_CREATED)
        node_id = res_comm.data["node_id"]

        # 2. Status API
        res_status = self.client.get("/api/matter/status/")
        self.assertEqual(res_status.status_code, status.HTTP_200_OK)
        self.assertEqual(res_status.data["status"], "online")
        self.assertGreaterEqual(res_status.data["nodes_count"], 1)

        # 3. Node Command API
        res_cmd = self.client.post(
            f"/api/matter/nodes/{node_id}/command/",
            {"command": "toggle"},
            format="json",
        )
        self.assertEqual(res_cmd.status_code, status.HTTP_200_OK)

        # 4. Telemetry Report API
        res_report = self.client.post(
            "/api/matter/telemetry/report/",
            {
                "node_id": node_id,
                "endpoint_id": 1,
                "cluster_id": "0x0090",
                "attributes": {"active_power_w": 2450.0},
            },
            format="json",
        )
        self.assertEqual(res_report.status_code, status.HTTP_200_OK)
        self.assertEqual(res_report.data["power_w"], 2450.0)

        # 5. Delete Node API
        res_del = self.client.delete(f"/api/matter/nodes/{node_id}/")
        self.assertEqual(res_del.status_code, status.HTTP_200_OK)
        self.assertEqual(res_del.data["status"], "deleted")

