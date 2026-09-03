###########################
# devices/tests_ocpp.py
###########################

import json
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator

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
        await communicator.send_json_to(stop_msg)
        res_stop = await communicator.receive_json_from()
        self.assertEqual(res_stop[0], 3)
        self.assertEqual(res_stop[2]["idTagInfo"]["status"], "Accepted")

        await communicator.disconnect()
