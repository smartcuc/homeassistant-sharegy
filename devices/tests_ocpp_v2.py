###############################
# devices/tests_ocpp_v2.py
# OCPP 2.0.1, OCPP 2.1 & V2G (ISO 15118-20) Tests
###############################

import json
import asyncio
from django.test import TransactionTestCase, TestCase
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from rest_framework.test import APIClient

from backend.asgi import application
from devices.models import Home
from devices.models_ocpp import ChargingStation, ChargingSession
from energy.services.services_v2g import V2GDispatchEngine

User = get_user_model()


class Ocpp2ProtocolTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ocpp2_user",
            email="ocpp2@sharegy.de",
            password="securepassword123"
        )
        self.home = Home.objects.create(
            user=self.user,
            name="OCPP 2.x Smart Home"
        )
        self.station = ChargingStation.objects.create(
            home=self.home,
            charge_point_id="CP-OCPP2-01",
            name="Alfen Eve Single Pro 2.0",
            max_current_a=16.0,
            smart_charging_mode="pv_surplus",
            supports_bidirectional=True,
            v2g_mode="v2h_home",
            v2g_min_soc_pct=40
        )

    async def test_ocpp201_boot_notification(self):
        """Testet OCPP 2.0.1 Subprotocol Negotiation & BootNotification."""
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/CP-OCPP2-01",
            subprotocols=["ocpp2.0.1", "ocpp1.6"]
        )
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        self.assertEqual(subprotocol, "ocpp2.0.1")

        boot_msg = [
            2,
            "boot-ocpp2-msg-1",
            "BootNotification",
            {
                "reason": "PowerUp",
                "chargingStation": {
                    "vendorName": "Alfen",
                    "model": "Eve Single Pro-Line",
                    "serialNumber": "ALF-2026-991",
                    "firmwareVersion": "v5.2.0-ocpp201"
                }
            }
        ]
        await communicator.send_json_to(boot_msg)
        response = await communicator.receive_json_from()

        self.assertEqual(response[0], 3)
        self.assertEqual(response[1], "boot-ocpp2-msg-1")
        self.assertEqual(response[2]["status"], "Accepted")
        self.assertEqual(response[2]["interval"], 60)

        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="CP-OCPP2-01")
        self.assertEqual(station.vendor, "Alfen")
        self.assertEqual(station.ocpp_version, "ocpp2.0.1")

        await communicator.disconnect()

    async def test_ocpp21_transaction_event_and_v2g_discharge(self):
        """Testet OCPP 2.1 TransactionEvent (Started, Updated, Ended) mit ISO 15118-20 SoC & V2G Export Power."""
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/CP-OCPP2-01",
            subprotocols=["ocpp2.1"]
        )
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        self.assertEqual(subprotocol, "ocpp2.1")

        # 1. TransactionEvent: Started mit ISO 15118 eMAID
        start_event = [
            2,
            "tx-event-start-1",
            "TransactionEvent",
            {
                "eventType": "Started",
                "timestamp": "2026-09-08T22:00:00Z",
                "triggerReason": "Authorized",
                "seqNo": 1,
                "transactionInfo": {
                    "transactionId": "TX-V2G-888999",
                    "chargingState": "Charging"
                },
                "idToken": {
                    "idToken": "DE-SHG-EMAID-99",
                    "type": "eMAID"
                },
                "evse": {"id": 1, "connectorId": 1},
                "meterValue": [
                    {
                        "timestamp": "2026-09-08T22:00:00Z",
                        "sampledValue": [
                            {"value": "10000", "measurand": "Energy.Active.Import.Register"}
                        ]
                    }
                ]
            }
        ]
        await communicator.send_json_to(start_event)
        res_start = await communicator.receive_json_from()
        self.assertEqual(res_start[0], 3)
        self.assertEqual(res_start[2]["idTokenInfo"]["status"], "Accepted")

        # 2. TransactionEvent: Updated mit V2G Entladung (Power.Active.Export = 4.5 kW) & ISO 15118 SoC (68%)
        update_event = [
            2,
            "tx-event-update-1",
            "TransactionEvent",
            {
                "eventType": "Updated",
                "timestamp": "2026-09-08T22:15:00Z",
                "triggerReason": "MeterValuePeriodic",
                "seqNo": 2,
                "transactionInfo": {
                    "transactionId": "TX-V2G-888999",
                    "chargingState": "Charging"
                },
                "evse": {"id": 1, "connectorId": 1},
                "meterValue": [
                    {
                        "timestamp": "2026-09-08T22:15:00Z",
                        "sampledValue": [
                            {"value": "4500", "measurand": "Power.Active.Export", "unit": "W"},
                            {"value": "68", "measurand": "SoC"}
                        ]
                    }
                ]
            }
        ]
        await communicator.send_json_to(update_event)
        res_update = await communicator.receive_json_from()
        self.assertEqual(res_update[0], 3)

        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="CP-OCPP2-01")
        self.assertEqual(station.v2g_discharge_power_w, 4500.0)
        self.assertEqual(station.ev_soc_pct, 68.0)
        self.assertTrue(station.is_discharging_v2g)

        # 3. TransactionEvent: Ended
        end_event = [
            2,
            "tx-event-end-1",
            "TransactionEvent",
            {
                "eventType": "Ended",
                "timestamp": "2026-09-08T23:00:00Z",
                "triggerReason": "EVDisconnected",
                "seqNo": 3,
                "transactionInfo": {
                    "transactionId": "TX-V2G-888999",
                    "chargingState": "Idle",
                    "stoppedReason": "EVDisconnected"
                },
                "evse": {"id": 1, "connectorId": 1},
                "meterValue": [
                    {
                        "timestamp": "2026-09-08T23:00:00Z",
                        "sampledValue": [
                            {"value": "10000", "measurand": "Energy.Active.Import.Register"},
                            {"value": "4500", "measurand": "Energy.Active.Export.Register"}
                        ]
                    }
                ]
            }
        ]
        await communicator.send_json_to(end_event)
        res_end = await communicator.receive_json_from()
        self.assertEqual(res_end[0], 3)

        station_after = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="CP-OCPP2-01")
        self.assertEqual(station_after.status, "Available")

        await communicator.disconnect()

    async def test_ocpp201_notify_event_device_model(self):
        """Testet NotifyEvent & Device Model Variable Reporting."""
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/CP-OCPP2-01",
            subprotocols=["ocpp2.0.1"]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        notify_msg = [
            2,
            "notify-ev-1",
            "NotifyEvent",
            {
                "generatedAt": "2026-09-08T22:30:00Z",
                "seqNo": 1,
                "eventData": [
                    {
                        "eventId": 101,
                        "timestamp": "2026-09-08T22:30:00Z",
                        "trigger": "Periodic",
                        "actualValue": "Installed",
                        "component": {"name": "ISO15118Ctrlr"},
                        "variable": {"name": "CertificateInstalled"}
                    },
                    {
                        "eventId": 102,
                        "timestamp": "2026-09-08T22:30:00Z",
                        "trigger": "Periodic",
                        "actualValue": "Available",
                        "component": {"name": "EVSE"},
                        "variable": {"name": "AvailabilityState"}
                    }
                ]
            }
        ]
        await communicator.send_json_to(notify_msg)
        res = await communicator.receive_json_from()
        self.assertEqual(res[0], 3)

        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="CP-OCPP2-01")
        self.assertIn("ISO15118Ctrlr.CertificateInstalled", station.device_variables)
        self.assertEqual(station.device_variables["ISO15118Ctrlr.CertificateInstalled"]["value"], "Installed")

        await communicator.disconnect()

    async def test_iso15118_certificate_request(self):
        """Testet Get15118EVCertificate Plug & Charge Contract Handshake."""
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/CP-OCPP2-01",
            subprotocols=["ocpp2.0.1"]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        cert_req = [
            2,
            "cert-req-1",
            "Get15118EVCertificate",
            {
                "iso15118SchemaVersion": "urn:iso:15118:20:CommonMessages",
                "action": "Install",
                "exiRequest": "80980200"
            }
        ]
        await communicator.send_json_to(cert_req)
        res = await communicator.receive_json_from()
        self.assertEqual(res[0], 3)
        self.assertEqual(res[2]["status"], "Accepted")

        await communicator.disconnect()

    async def test_ocpp2_steering_commands(self):
        """Testet OCPP 2.0.1 Steuersignale: SetChargingProfile, ClearChargingProfile, ChangeAvailability."""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()

        communicator = WebsocketCommunicator(
            application,
            "/ocpp/CP-OCPP2-01",
            subprotocols=["ocpp2.0.1"]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # 1. SetChargingProfile Event über Channel Layer
        await channel_layer.group_send(
            "ocpp_CP-OCPP2-01",
            {"type": "ocpp_set_charging_profile", "current_a": 12.0, "connector_id": 1}
        )
        msg_set = await communicator.receive_json_from()
        self.assertEqual(msg_set[0], 2)
        self.assertEqual(msg_set[2], "SetChargingProfile")
        # In OCPP 2.0.1 muss evseId & chargingProfile vorhanden sein
        self.assertEqual(msg_set[3]["evseId"], 1)
        self.assertIn("chargingProfile", msg_set[3])
        self.assertEqual(msg_set[3]["chargingProfile"]["chargingSchedule"][0]["chargingSchedulePeriod"][0]["limit"], 12.0)

        # 2. ClearChargingProfile Event
        await channel_layer.group_send(
            "ocpp_CP-OCPP2-01",
            {"type": "ocpp_clear_charging_profile", "charging_profile_id": 1, "connector_id": 1}
        )
        msg_clear = await communicator.receive_json_from()
        self.assertEqual(msg_clear[0], 2)
        self.assertEqual(msg_clear[2], "ClearChargingProfile")
        self.assertEqual(msg_clear[3]["chargingProfileId"], 1)
        self.assertEqual(msg_clear[3]["chargingProfileCriteria"]["evseId"], 1)

        # 3. ChangeAvailability Event
        await channel_layer.group_send(
            "ocpp_CP-OCPP2-01",
            {"type": "ocpp_change_availability", "availability_type": "Inoperative", "connector_id": 1}
        )
        msg_avail = await communicator.receive_json_from()
        self.assertEqual(msg_avail[0], 2)
        self.assertEqual(msg_avail[2], "ChangeAvailability")
        self.assertEqual(msg_avail[3]["operationalStatus"], "Inoperative")
        self.assertEqual(msg_avail[3]["evse"]["id"], 1)

        # 4. GetCompositeSchedule Event
        await channel_layer.group_send(
            "ocpp_CP-OCPP2-01",
            {"type": "ocpp_get_composite_schedule", "duration": 3600, "charging_rate_unit": "W", "connector_id": 1}
        )
        msg_sched = await communicator.receive_json_from()
        self.assertEqual(msg_sched[0], 2)
        self.assertEqual(msg_sched[2], "GetCompositeSchedule")
        self.assertEqual(msg_sched[3]["evseId"], 1)
        self.assertEqual(msg_sched[3]["duration"], 3600)

        await communicator.disconnect()


class V2GDispatchEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="v2g_algo_user", email="v2g@sharegy.de")
        self.home = Home.objects.create(user=self.user, name="V2G Home")
        self.station = ChargingStation.objects.create(
            home=self.home,
            charge_point_id="CP-V2G-ALGO",
            name="V2G Station",
            supports_bidirectional=True,
            v2g_mode="v2h_home",
            v2g_min_soc_pct=50,
            v2g_max_discharge_power_kw=11.0,
            ev_soc_pct=75.0,
            phases=3
        )

    def test_v2h_home_backup_dispatches_when_pv_zero_and_load_high(self):
        class DummyMetric:
            pv_power_w = 0.0
            house_power_w = 3450.0  # 3.45 kW Hausverbrauch
            battery_soc_pct = 15.0  # Heimspeicher leer
            battery_power_w = 0.0

        res = V2GDispatchEngine.calculate_v2x_dispatch(self.station, DummyMetric(), spot_price_eur_mwh=120.0)
        self.assertEqual(res["mode"], "discharging")
        self.assertEqual(res["target_power_w"], -3450.0)
        self.assertEqual(res["target_current_a"], 5.0)  # 3450W / (230V * 3) = 5A
        self.assertFalse(res["soc_protected"])

    def test_v2h_protects_ev_battery_when_soc_below_min_threshold(self):
        self.station.ev_soc_pct = 45.0  # unter 50% Mindest-SoC
        self.station.save()

        class DummyMetric:
            pv_power_w = 0.0
            house_power_w = 4000.0
            battery_soc_pct = 10.0
            battery_power_w = 0.0

        res = V2GDispatchEngine.calculate_v2x_dispatch(self.station, DummyMetric(), spot_price_eur_mwh=150.0)
        self.assertEqual(res["mode"], "idle")
        self.assertEqual(res["target_power_w"], 0.0)
        self.assertTrue(res["soc_protected"])

    def test_v2g_arbitrage_feeds_in_on_extreme_prices(self):
        self.station.v2g_mode = "v2g_grid"
        self.station.ev_soc_pct = 80.0
        self.station.save()

        class DummyMetric:
            pv_power_w = 0.0
            house_power_w = 500.0
            battery_soc_pct = 100.0
            battery_power_w = 0.0

        # Spotpreis extrem hoch: 450 €/MWh = 45.0 ct/kWh
        res = V2GDispatchEngine.calculate_v2x_dispatch(self.station, DummyMetric(), spot_price_eur_mwh=450.0)
        self.assertEqual(res["mode"], "discharging")
        self.assertEqual(res["target_power_w"], -11000.0)  # Volle 11 kW Entladung ins Netz!


class V2GRestApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="v2g_api_user", email="v2gapi@sharegy.de")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.home = Home.objects.create(user=self.user, name="V2G API Home")
        self.station = ChargingStation.objects.create(
            home=self.home,
            charge_point_id="CP-V2G-REST",
            name="V2G API Box",
            supports_bidirectional=True
        )

    def test_set_v2g_mode_and_manual_discharge_endpoints(self):
        # 1. Set V2G Mode
        res_mode = self.client.post(
            f"/api/energy/wallboxes/{self.station.id}/set-v2g-mode/",
            {
                "v2g_mode": "v2x_auto",
                "v2g_min_soc_pct": 55,
                "v2g_max_discharge_power_kw": 9.5
            },
            format="json"
        )
        self.assertEqual(res_mode.status_code, 200)
        self.station.refresh_from_db()
        self.assertEqual(self.station.v2g_mode, "v2x_auto")
        self.assertEqual(self.station.v2g_min_soc_pct, 55)
        self.assertEqual(self.station.v2g_max_discharge_power_kw, 9.5)

        # 2. Manual V2G Discharge Trigger
        res_dis = self.client.post(
            f"/api/energy/wallboxes/{self.station.id}/v2g-discharge/",
            {"power_w": 5000.0},
            format="json"
        )
        self.assertEqual(res_dis.status_code, 200)
        self.station.refresh_from_db()
        self.assertEqual(self.station.v2g_discharge_power_w, 5000.0)
        self.assertEqual(self.station.active_power_w, 0.0)

        # 3. GetVariables (OCPP 2.0.1 / 2.1)
        res_vars = self.client.post(f"/api/energy/wallboxes/{self.station.id}/get-variables/")
        self.assertEqual(res_vars.status_code, 200)
