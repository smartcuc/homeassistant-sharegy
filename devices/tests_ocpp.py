###########################
# devices/tests_ocpp.py
###########################

import json
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from backend.asgi import application
from devices.models import Home
from devices.models_ocpp import ChargingStation, ChargingSession, ChargingRfidTag

User = get_user_model()


class OcppConsumerTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ocppuser",
            email="ocpp@sharegy.de",
            password="securepassword123"
        )
        self.home = Home.objects.create(
            user=self.user,
            name="OCPP Test Home"
        )
        self.station = ChargingStation.objects.create(
            home=self.home,
            charge_point_id="TEST-CP-01",
            name="Easee Home Box",
            max_current_a=16.0,
            smart_charging_mode="pv_surplus"
        )

    async def test_ocpp_boot_notification(self):
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/TEST-CP-01",
            subprotocols=["ocpp1.6"]
        )
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        self.assertEqual(subprotocol, "ocpp1.6")

        # BootNotification senden
        boot_msg = [
            2,
            "boot-uuid-1",
            "BootNotification",
            {
                "chargePointVendor": "Easee",
                "chargePointModel": "Charge",
                "chargePointSerialNumber": "ES-9988",
                "firmwareVersion": "v3.1.2"
            }
        ]
        await communicator.send_json_to(boot_msg)
        response = await communicator.receive_json_from()

        self.assertEqual(response[0], 3)
        self.assertEqual(response[1], "boot-uuid-1")
        self.assertEqual(response[2]["status"], "Accepted")
        self.assertEqual(response[2]["interval"], 60)

        await communicator.disconnect()

    async def test_ocpp_status_and_meter_values(self):
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/TEST-CP-01",
            subprotocols=["ocpp1.6"]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # StatusNotification: Charging
        status_msg = [
            2,
            "status-1",
            "StatusNotification",
            {"connectorId": 1, "status": "Charging", "errorCode": "NoError"}
        ]
        await communicator.send_json_to(status_msg)
        res1 = await communicator.receive_json_from()
        self.assertEqual(res1[0], 3)

        # MeterValues: 7.4 kW, 16A auf L1/L2/L3, 12.5 kWh
        mv_msg = [
            2,
            "mv-1",
            "MeterValues",
            {
                "connectorId": 1,
                "meterValue": [
                    {
                        "timestamp": "2026-09-03T04:00:00Z",
                        "sampledValue": [
                            {"value": "7400", "measurand": "Power.Active.Import", "unit": "W"},
                            {"value": "16.0", "measurand": "Current.Import", "phase": "L1"},
                            {"value": "16.0", "measurand": "Current.Import", "phase": "L2"},
                            {"value": "16.0", "measurand": "Current.Import", "phase": "L3"},
                            {"value": "12500", "measurand": "Energy.Active.Import.Register", "unit": "Wh"}
                        ]
                    }
                ]
            }
        ]
        await communicator.send_json_to(mv_msg)
        res2 = await communicator.receive_json_from()
        self.assertEqual(res2[0], 3)

        await communicator.disconnect()

    async def test_ocpp_start_and_stop_transaction(self):
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/TEST-CP-01",
            subprotocols=["ocpp1.6"]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # StartTransaction
        start_msg = [
            2,
            "tx-start-1",
            "StartTransaction",
            {
                "connectorId": 1,
                "idTag": "TAG_NEIGHBOR_1",
                "meterStart": 10000,
                "timestamp": "2026-09-03T04:10:00Z"
            }
        ]
        await communicator.send_json_to(start_msg)
        res_start = await communicator.receive_json_from()
        self.assertEqual(res_start[0], 3)
        tx_id = res_start[2]["transactionId"]
        self.assertTrue(tx_id > 0)
        self.assertEqual(res_start[2]["idTagInfo"]["status"], "Accepted")

        # StopTransaction mit 25 kWh geladen
        stop_msg = [
            2,
            "tx-stop-1",
            "StopTransaction",
            {
                "transactionId": tx_id,
                "meterStop": 35000,
                "timestamp": "2026-09-03T06:10:00Z",
                "reason": "EVDisconnected",
                "idTag": "TAG_NEIGHBOR_1"
            }
        ]
        await communicator.disconnect()

    async def test_ocpp_reserved_status_handling(self):
        """Testet, dass eine reservierte Station nicht autorisierte Ladevorgänge abweist."""
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/TEST-CP-01",
            subprotocols=["ocpp1.6"]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # 1. Station auf 'Reserved' für TAG_OWNER setzen via StatusNotification
        status_msg = [
            2,
            "status-res-1",
            "StatusNotification",
            {"connectorId": 1, "status": "Reserved", "errorCode": "NoError"}
        ]
        await communicator.send_json_to(status_msg)
        await communicator.receive_json_from()

        # Station DB-Status prüfen
        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertEqual(station.status, "Reserved")
        self.assertEqual(station.active_power_w, 0.0)

        # Reservierungstag manuell in DB hinterlegen
        station.reserved_id_tag = "TAG_RESERVED_VIP"
        await database_sync_to_async(station.save)()

        # 2. StartTransaction mit falschem Tag versuchen -> Muss abgelehnt (Blocked) werden
        start_wrong = [
            2,
            "tx-start-wrong",
            "StartTransaction",
            {
                "connectorId": 1,
                "idTag": "TAG_STRANGER",
                "meterStart": 0,
                "timestamp": "2026-09-03T04:10:00Z"
            }
        ]
        await communicator.send_json_to(start_wrong)
        res_wrong = await communicator.receive_json_from()
        self.assertEqual(res_wrong[0], 3)
        self.assertEqual(res_wrong[2]["idTagInfo"]["status"], "Blocked")

        # 3. MeterValues empfangen während 'Reserved' -> darf Status NICHT auf 'Charging' überschreiben!
        mv_msg = [
            2,
            "mv-res-1",
            "MeterValues",
            {
                "connectorId": 1,
                "meterValue": [
                    {
                        "timestamp": "2026-09-03T04:12:00Z",
                        "sampledValue": [
                            {"value": "3500", "measurand": "Power.Active.Import", "unit": "W"}
                        ]
                    }
                ]
            }
        ]
        await communicator.send_json_to(mv_msg)
        await communicator.receive_json_from()

        station_after_mv = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertEqual(station_after_mv.status, "Reserved")

        # 4. StartTransaction mit passendem Reservierungs-Tag -> Wird akzeptiert!
        start_correct = [
            2,
            "tx-start-correct",
            "StartTransaction",
            {
                "connectorId": 1,
                "idTag": "TAG_RESERVED_VIP",
                "meterStart": 0,
                "timestamp": "2026-09-03T04:15:00Z"
            }
        ]
        await communicator.send_json_to(start_correct)
        res_correct = await communicator.receive_json_from()
        self.assertEqual(res_correct[0], 3)
        self.assertEqual(res_correct[2]["idTagInfo"]["status"], "Accepted")
        self.assertTrue(res_correct[2]["transactionId"] > 0)

        await communicator.disconnect()

    async def test_ocpp16_remote_start_and_stop_flow(self):
        """Testet RemoteStartTransaction und RemoteStopTransaction in OCPP 1.6."""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()

        communicator = WebsocketCommunicator(
            application,
            "/ocpp/TEST-CP-01",
            subprotocols=["ocpp1.6"]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # 1. Server sendet ocpp_remote_start
        await channel_layer.group_send(
            "ocpp_TEST-CP-01",
            {"type": "ocpp_remote_start", "connector_id": 1, "id_tag": "APP_USER_16"}
        )
        msg_start = await communicator.receive_json_from()
        self.assertEqual(msg_start[0], 2)
        self.assertEqual(msg_start[2], "RemoteStartTransaction")
        self.assertEqual(msg_start[3]["connectorId"], 1)
        self.assertEqual(msg_start[3]["idTag"], "APP_USER_16")
        call_id = msg_start[1]

        # 2. Station antwortet Accepted
        await communicator.send_json_to([3, call_id, {"status": "Accepted"}])

        # 3. Station sendet StartTransaction
        start_msg = [
            2,
            "tx-16-start",
            "StartTransaction",
            {
                "connectorId": 1,
                "idTag": "APP_USER_16",
                "meterStart": 1000,
                "timestamp": "2026-09-03T05:00:00Z"
            }
        ]
        await communicator.send_json_to(start_msg)
        res_start = await communicator.receive_json_from()
        self.assertEqual(res_start[0], 3)
        tx_id = res_start[2]["transactionId"]
        self.assertTrue(tx_id > 0)
        self.assertEqual(res_start[2]["idTagInfo"]["status"], "Accepted")

        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertEqual(station.status, "Charging")
        self.assertTrue(station.is_charging)

        # 4. Server sendet ocpp_remote_stop
        await channel_layer.group_send(
            "ocpp_TEST-CP-01",
            {"type": "ocpp_remote_stop", "transaction_id": tx_id}
        )
        msg_stop = await communicator.receive_json_from()
        self.assertEqual(msg_stop[0], 2)
        self.assertEqual(msg_stop[2], "RemoteStopTransaction")
        self.assertEqual(msg_stop[3]["transactionId"], tx_id)
        call_stop_id = msg_stop[1]

        # 5. Station antwortet Accepted
        await communicator.send_json_to([3, call_stop_id, {"status": "Accepted"}])

        # 6. Station sendet StopTransaction
        stop_msg = [
            2,
            "tx-16-stop",
            "StopTransaction",
            {
                "transactionId": tx_id,
                "meterStop": 6000,
                "timestamp": "2026-09-03T05:30:00Z",
                "reason": "Remote",
                "idTag": "APP_USER_16"
            }
        ]
        await communicator.send_json_to(stop_msg)
        res_stop = await communicator.receive_json_from()
        self.assertEqual(res_stop[0], 3)

        station_done = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertEqual(station_done.status, "Available")
        self.assertFalse(station_done.is_charging)

        await communicator.disconnect()

    async def test_ocpp_diagnostics_and_firmware_notifications(self):
        """Testet DiagnosticsStatusNotification & FirmwareStatusNotification Handling."""
        communicator = WebsocketCommunicator(
            application,
            "/ocpp/TEST-CP-01",
            subprotocols=["ocpp1.6"]
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # 1. DiagnosticsStatusNotification: Uploading
        diag_msg = [
            2,
            "diag-1",
            "DiagnosticsStatusNotification",
            {"status": "Uploading"}
        ]
        await communicator.send_json_to(diag_msg)
        res1 = await communicator.receive_json_from()
        self.assertEqual(res1[0], 3)
        self.assertEqual(res1[1], "diag-1")

        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertEqual(station.diagnostics_status, "Uploading")

        # 2. DiagnosticsStatusNotification: Uploaded
        diag_done_msg = [
            2,
            "diag-2",
            "DiagnosticsStatusNotification",
            {"status": "Uploaded"}
        ]
        await communicator.send_json_to(diag_done_msg)
        res2 = await communicator.receive_json_from()
        self.assertEqual(res2[0], 3)

        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertEqual(station.diagnostics_status, "Uploaded")

        # 3. CallResult von GetDiagnostics mit Dateinamen
        call_res_diag = [
            3,
            "msg-diag-req-1",
            {"fileName": "diagnostics_20260908_TEST-CP-01.log"}
        ]
        await communicator.send_json_to(call_res_diag)
        import asyncio
        await asyncio.sleep(0.1)
        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertEqual(station.last_diagnostics_file, "diagnostics_20260908_TEST-CP-01.log")

        # 4. CallResult von GetLocalListVersion
        call_res_local_list = [
            3,
            "msg-local-list-req-1",
            {"listVersion": 4}
        ]
        await communicator.send_json_to(call_res_local_list)
        await asyncio.sleep(0.1)
        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertEqual(station.local_auth_list_version, 4)

        # 5. CallResult von GetCompositeSchedule
        call_res_schedule = [
            3,
            "msg-sched-req-1",
            {
                "status": "Accepted",
                "connectorId": 1,
                "scheduleStart": "2026-09-08T22:00:00Z",
                "chargingSchedule": {
                    "duration": 86400,
                    "chargingRateUnit": "A",
                    "chargingSchedulePeriod": [
                        {"startPeriod": 0, "limit": 16.0, "numberPhases": 3}
                    ]
                }
            }
        ]
        await communicator.send_json_to(call_res_schedule)
        await asyncio.sleep(0.1)
        station = await database_sync_to_async(ChargingStation.objects.get)(charge_point_id="TEST-CP-01")
        self.assertIsNotNone(station.composite_schedule_data)
        self.assertEqual(station.composite_schedule_data.get("status"), "Accepted")

        await communicator.disconnect()


from django.test import TestCase
from rest_framework.test import APIClient

class OcppRestApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ocpp_api_user",
            email="ocppapi@sharegy.de",
            password="securepassword123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.home = Home.objects.create(
            user=self.user,
            name="API Test Home"
        )
        self.station = ChargingStation.objects.create(
            home=self.home,
            charge_point_id="TEST-API-CP-01",
            name="API Test Wallbox",
            max_current_a=16.0,
            smart_charging_mode="pv_surplus"
        )
        self.rfid = ChargingRfidTag.objects.create(
            home=self.home,
            id_tag="RFID_12345",
            name="Familienauto"
        )

    def test_wallbox_remote_action_endpoints(self):
        # 1. Trigger Message
        res_trigger = self.client.post(
            f"/api/energy/wallboxes/{self.station.id}/trigger-message/",
            {"requested_message": "MeterValues"},
            format="json"
        )
        self.assertEqual(res_trigger.status_code, 200)

        # 2. Get Local List Version
        res_ll_ver = self.client.post(f"/api/energy/wallboxes/{self.station.id}/get-local-list-version/")
        self.assertEqual(res_ll_ver.status_code, 200)

        # 3. Sync RFID List
        res_sync_rfid = self.client.post(
            f"/api/energy/wallboxes/{self.station.id}/sync-rfid-list/",
            {"update_type": "Full"},
            format="json"
        )
        self.assertEqual(res_sync_rfid.status_code, 200)

        # 4. Get Composite Schedule
        res_sched = self.client.post(
            f"/api/energy/wallboxes/{self.station.id}/get-composite-schedule/",
            {"duration": 86400},
            format="json"
        )
        self.assertEqual(res_sched.status_code, 200)

        # 5. Clear Charging Profile
        res_clear_prof = self.client.post(
            f"/api/energy/wallboxes/{self.station.id}/clear-charging-profile/",
            {"profile_id": 1},
            format="json"
        )
        self.assertEqual(res_clear_prof.status_code, 200)

        # 6. Reserve Now
        res_reserve = self.client.post(
            f"/api/energy/wallboxes/{self.station.id}/reserve/",
            {"id_tag": "RFID_12345", "duration_minutes": 60},
            format="json"
        )
        self.assertEqual(res_reserve.status_code, 200)
        self.station.refresh_from_db()
        self.assertEqual(self.station.status, "Reserved")
        self.assertEqual(self.station.reserved_id_tag, "RFID_12345")

        # 7. Cancel Reservation
        res_cancel = self.client.post(f"/api/energy/wallboxes/{self.station.id}/cancel-reserve/")
        self.assertEqual(res_cancel.status_code, 200)
        self.station.refresh_from_db()
        self.assertEqual(self.station.status, "Available")
        self.assertEqual(self.station.reserved_id_tag, "")
        self.assertIsNone(self.station.reservation_id)

        # 8. Get Diagnostics
        res_diag = self.client.post(
            f"/api/energy/wallboxes/{self.station.id}/get-diagnostics/",
            {"target_url": "ftp://upload.sharegy.de/diagnostics/"},
            format="json"
        )
        self.assertEqual(res_diag.status_code, 200)

    def test_rfid_tag_crud_endpoints(self):
        # 1. List Tags
        res_list = self.client.get("/api/energy/rfid-tags/")
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(len(res_list.json()["rfid_tags"]), 1)

        # 2. Create Tag
        res_create = self.client.post(
            "/api/energy/rfid-tags/",
            {"name": "Zweitwagen Chip", "id_tag": "TAG-998877", "is_active": True},
            format="json"
        )
        self.assertEqual(res_create.status_code, 201)
        tag_id = res_create.json()["rfid_tag"]["id"]

        # 3. Patch Tag (Toggle active)
        res_patch = self.client.patch(
            f"/api/energy/rfid-tags/{tag_id}/",
            {"is_active": False, "name": "Gesperrter Chip"},
            format="json"
        )
        self.assertEqual(res_patch.status_code, 200)
        self.assertFalse(res_patch.json()["rfid_tag"]["is_active"])
        self.assertEqual(res_patch.json()["rfid_tag"]["name"], "Gesperrter Chip")

        # 4. Delete Tag
        res_del = self.client.delete(f"/api/energy/rfid-tags/{tag_id}/")
        self.assertEqual(res_del.status_code, 200)
        self.assertFalse(ChargingRfidTag.objects.filter(id=tag_id).exists())

