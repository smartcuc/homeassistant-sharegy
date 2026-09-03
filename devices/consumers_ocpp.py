#############################
# devices/consumers_ocpp.py
#############################

import json
import logging
import uuid
from decimal import Decimal
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger("django")

CALL = 2
CALLRESULT = 3
CALLERROR = 4


class OcppConsumer(AsyncWebsocketConsumer):
    """
    OCPP 1.6-J (JSON over WebSocket) CSMS Gateway.
    Verbindet Wallboxen (Easee, go-e, Keba, Alfen, Mennekes, Zaptec, etc.)
    direkt mit der Sharegy Cloud für intelligentes PV-Überschuss- und Börsenstrom-Laden.
    """

    async def connect(self):
        self.cp_id = self.scope["url_route"]["kwargs"].get("cp_id", "default_cp").strip()
        self.group_name = f"ocpp_{self.cp_id}"
        self.home_group = None

        # OCPP 1.6 Subprotocol aushandeln
        subprotocols = self.scope.get("subprotocols", [])
        selected_subprotocol = None
        if "ocpp1.6" in subprotocols:
            selected_subprotocol = "ocpp1.6"
        elif "ocpp2.0.1" in subprotocols:
            selected_subprotocol = "ocpp2.0.1"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept(subprotocol=selected_subprotocol)

        # Station in DB online setzen
        station_info = await self.get_or_create_station(self.cp_id)
        if station_info and station_info.get("home_id"):
            self.home_group = f"home_{station_info['home_id']}"
            await self.channel_layer.group_add(self.home_group, self.channel_name)

        logger.info(f"⚡ OCPP-Wallbox verbunden: {self.cp_id} (Subprotocol: {selected_subprotocol})")

    async def disconnect(self, close_code):
        await self.set_station_offline(self.cp_id)
        if self.home_group:
            await self.channel_layer.group_discard(self.home_group, self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"🔌 OCPP-Wallbox getrennt: {self.cp_id} (Code: {close_code})")

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            msg = json.loads(text_data)
            if not isinstance(msg, list) or len(msg) < 3:
                return

            msg_type = msg[0]
            unique_id = msg[1]

            if msg_type == CALL:
                action = msg[2]
                payload = msg[3] if len(msg) > 3 else {}
                await self.handle_ocpp_call(unique_id, action, payload)

            elif msg_type == CALLRESULT:
                payload = msg[2] if len(msg) > 2 else {}
                logger.debug(f"OCPP CallResult von {self.cp_id} für {unique_id}: {payload}")

            elif msg_type == CALLERROR:
                error_code = msg[2]
                error_desc = msg[3] if len(msg) > 3 else ""
                logger.warning(f"OCPP CallError von {self.cp_id} für {unique_id}: [{error_code}] {error_desc}")

        except Exception as e:
            logger.error(f"Fehler bei OCPP Nachricht von {self.cp_id}: {e}", exc_info=True)

    async def handle_ocpp_call(self, unique_id: str, action: str, payload: dict):
        """Verarbeitet eingehende OCPP 1.6-J Aufrufe der Wallbox."""
        now_iso = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if action == "BootNotification":
            vendor = payload.get("chargePointVendor", "")
            model = payload.get("chargePointModel", "")
            serial = payload.get("chargePointSerialNumber", "")
            fw = payload.get("firmwareVersion", "")
            await self.update_boot_notification(self.cp_id, vendor, model, serial, fw)

            res = {
                "currentTime": now_iso,
                "interval": 60,
                "status": "Accepted",
            }
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "Heartbeat":
            await self.update_heartbeat(self.cp_id)
            res = {"currentTime": now_iso}
            await self.send_call_result(unique_id, res)

        elif action == "StatusNotification":
            connector_id = payload.get("connectorId", 1)
            status = payload.get("status", "Available")
            error_code = payload.get("errorCode", "NoError")
            await self.update_status(self.cp_id, connector_id, status, error_code)

            res = {}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "MeterValues":
            connector_id = payload.get("connectorId", 1)
            tx_id = payload.get("transactionId")
            meter_values = payload.get("meterValue", [])
            await self.process_meter_values(self.cp_id, connector_id, tx_id, meter_values)

            res = {}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "Authorize":
            id_tag = payload.get("idTag", "")
            is_valid = await self.validate_rfid_tag(self.cp_id, id_tag)
            res = {
                "idTagInfo": {
                    "status": "Accepted" if is_valid else "Invalid",
                    "expiryDate": (timezone.now() + timezone.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
            }
            await self.send_call_result(unique_id, res)

        elif action == "StartTransaction":
            connector_id = payload.get("connectorId", 1)
            id_tag = payload.get("idTag", "")
            meter_start = payload.get("meterStart", 0)
            tx_id = await self.create_start_transaction(self.cp_id, connector_id, id_tag, meter_start)

            res = {
                "transactionId": tx_id,
                "idTagInfo": {"status": "Accepted"}
            }
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "StopTransaction":
            tx_id = payload.get("transactionId")
            meter_stop = payload.get("meterStop", 0)
            reason = payload.get("reason", "Local")
            id_tag = payload.get("idTag", "")
            await self.finish_stop_transaction(self.cp_id, tx_id, meter_stop, reason, id_tag)

            res = {"idTagInfo": {"status": "Accepted"}}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action in ["DataTransfer", "DiagnosticsStatusNotification", "FirmwareStatusNotification"]:
            res = {"status": "Accepted"}
            await self.send_call_result(unique_id, res)

        else:
            logger.info(f"Unbehandelte OCPP Action '{action}' von {self.cp_id}")
            res = {}
            await self.send_call_result(unique_id, res)

    async def send_call_result(self, unique_id: str, payload: dict):
        """Sendet ein OCPP 1.6 CALLRESULT [3, unique_id, payload]."""
        msg = [CALLRESULT, unique_id, payload]
        await self.send(text_data=json.dumps(msg))

    async def send_call(self, action: str, payload: dict):
        """Sendet einen OCPP 1.6 CALL [2, unique_id, action, payload] an die Wallbox."""
        unique_id = str(uuid.uuid4())
        msg = [CALL, unique_id, action, payload]
        await self.send(text_data=json.dumps(msg))
        return unique_id

    # ============================================================
    # 📡 CHANNEL LAYER HANDLER (VON REST-API ODER SMART CHARGER)
    # ============================================================

    async def ocpp_set_charging_profile(self, event):
        """Setzt dynamisch den Ladestrom in Ampere (z.B. 6A bis 16A/32A)."""
        current_limit_a = float(event.get("current_a", 16.0))
        connector_id = int(event.get("connector_id", 1))

        payload = {
            "connectorId": connector_id,
            "csChargingProfiles": {
                "chargingProfileId": 1,
                "stackLevel": 1,
                "chargingProfilePurpose": "TxDefaultProfile",
                "chargingProfileKind": "Relative",
                "chargingSchedule": {
                    "chargingRateUnit": "A",
                    "chargingSchedulePeriod": [
                        {
                            "startPeriod": 0,
                            "limit": current_limit_a,
                            "numberPhases": 3
                        }
                    ]
                }
            }
        }
        await self.send_call("SetChargingProfile", payload)
        await self.update_target_current(self.cp_id, current_limit_a)
        logger.info(f"⚡ OCPP SetChargingProfile gesendet an {self.cp_id}: {current_limit_a} A")

    async def ocpp_remote_start(self, event):
        """Startet den Ladevorgang aus der Sharegy App heraus."""
        connector_id = int(event.get("connector_id", 1))
        id_tag = event.get("id_tag", "SHAREGY_APP")
        payload = {
            "connectorId": connector_id,
            "idTag": id_tag
        }
        await self.send_call("RemoteStartTransaction", payload)
        logger.info(f"▶️ RemoteStartTransaction an {self.cp_id} (Tag: {id_tag})")

    async def ocpp_remote_stop(self, event):
        """Stoppt die aktive Ladesitzung."""
        tx_id = int(event.get("transaction_id", 0))
        if tx_id:
            payload = {"transactionId": tx_id}
            await self.send_call("RemoteStopTransaction", payload)
            logger.info(f"⏹️ RemoteStopTransaction an {self.cp_id} (Tx: {tx_id})")

    async def ocpp_unlock_connector(self, event):
        """Entriegelt das Ladekabel."""
        connector_id = int(event.get("connector_id", 1))
        payload = {"connectorId": connector_id}
        await self.send_call("UnlockConnector", payload)
        logger.info(f"🔓 UnlockConnector an {self.cp_id} (Connector: {connector_id})")

    async def wallbox_update(self, event):
        """No-op for the wallbox connection itself when broadcasting UI telemetry."""
        pass

    async def energy_update(self, event):
        """No-op for the wallbox connection itself when broadcasting UI telemetry."""
        pass

    # ============================================================
    # 🗄️ DATABASE SYNC TO ASYNC HELPER
    # ============================================================

    @database_sync_to_async
    def get_or_create_station(self, cp_id: str):
        from .models_ocpp import ChargingStation
        from .models import Home
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            home = Home.objects.first()
            if not home:
                return None
            station = ChargingStation.objects.create(
                home=home,
                charge_point_id=cp_id,
                name=f"Wallbox {cp_id}",
                is_online=True,
                last_heartbeat=timezone.now()
            )
        else:
            station.is_online = True
            station.last_heartbeat = timezone.now()
            station.save(update_fields=["is_online", "last_heartbeat"])
        return {"home_id": str(station.home_id), "id": str(station.id)}

    @database_sync_to_async
    def set_station_offline(self, cp_id: str):
        from .models_ocpp import ChargingStation
        ChargingStation.objects.filter(charge_point_id=cp_id).update(
            is_online=False,
            last_heartbeat=timezone.now()
        )

    @database_sync_to_async
    def update_boot_notification(self, cp_id, vendor, model, serial, fw):
        from .models_ocpp import ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if station:
            station.vendor = vendor
            station.model = model
            station.serial_number = serial
            station.firmware_version = fw
            station.is_online = True
            station.last_heartbeat = timezone.now()
            station.save(update_fields=["vendor", "model", "serial_number", "firmware_version", "is_online", "last_heartbeat"])

    @database_sync_to_async
    def update_heartbeat(self, cp_id):
        from .models_ocpp import ChargingStation
        ChargingStation.objects.filter(charge_point_id=cp_id).update(
            is_online=True,
            last_heartbeat=timezone.now()
        )

    @database_sync_to_async
    def update_status(self, cp_id, connector_id, status, error_code):
        from .models_ocpp import ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if station:
            station.status = status
            station.error_code = error_code
            station.is_online = True
            station.last_heartbeat = timezone.now()
            if status in ["Available", "Faulted", "Unavailable"]:
                station.active_power_w = 0.0
                station.current_l1 = 0.0
                station.current_l2 = 0.0
                station.current_l3 = 0.0
            station.save(update_fields=["status", "error_code", "is_online", "last_heartbeat", "active_power_w", "current_l1", "current_l2", "current_l3"])

    @database_sync_to_async
    def process_meter_values(self, cp_id, connector_id, tx_id, meter_values):
        from .models_ocpp import ChargingStation, ChargingSession
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return

        power_w = 0.0
        current_l1 = 0.0
        current_l2 = 0.0
        current_l3 = 0.0
        voltage_v = 230.0
        energy_wh = None

        for mv in meter_values:
            sampled_values = mv.get("sampledValue", [])
            for sv in sampled_values:
                measurand = sv.get("measurand", "Energy.Active.Import.Register")
                val_str = sv.get("value", "0")
                phase = sv.get("phase")
                unit = sv.get("unit", "")
                try:
                    val = float(val_str)
                except ValueError:
                    continue

                if measurand == "Power.Active.Import":
                    power_w = val * 1000.0 if unit.lower() in ["kw", "kvar"] else val
                elif measurand == "Current.Import":
                    if phase == "L1":
                        current_l1 = val
                    elif phase == "L2":
                        current_l2 = val
                    elif phase == "L3":
                        current_l3 = val
                    else:
                        current_l1 = val
                elif measurand == "Voltage":
                    voltage_v = val
                elif measurand in ["Energy.Active.Import.Register", "Energy.Active.Import.Interval"]:
                    energy_wh = val * 1000.0 if unit.lower() in ["kwh", "kvarh"] else val

        station.active_power_w = power_w
        station.current_l1 = current_l1
        station.current_l2 = current_l2
        station.current_l3 = current_l3
        station.voltage_v = voltage_v
        if power_w > 50.0:
            station.status = "Charging"

        if energy_wh is not None:
            station.total_energy_kwh = round(energy_wh / 1000.0, 3)

        # Aktive Session aktualisieren
        if tx_id:
            session = ChargingSession.objects.filter(station=station, transaction_id=tx_id, status="active").first()
            if session:
                if energy_wh is not None:
                    session_kwh = max(0.0, (energy_wh - session.meter_start_wh) / 1000.0)
                    session.total_energy_kwh = round(session_kwh, 2)
                    station.session_energy_kwh = session.total_energy_kwh
                    session.save(update_fields=["total_energy_kwh"])

        station.last_heartbeat = timezone.now()
        station.save(update_fields=[
            "active_power_w", "current_l1", "current_l2", "current_l3",
            "voltage_v", "status", "total_energy_kwh", "session_energy_kwh", "last_heartbeat"
        ])

    @database_sync_to_async
    def validate_rfid_tag(self, cp_id, id_tag):
        from .models_ocpp import ChargingRfidTag, ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return True
        # Wenn keine Tags eingerichtet sind, alle akzeptieren
        tags_count = ChargingRfidTag.objects.filter(home=station.home).count()
        if tags_count == 0:
            return True
        tag = ChargingRfidTag.objects.filter(home=station.home, id_tag=id_tag, is_active=True).first()
        return bool(tag)

    @database_sync_to_async
    def create_start_transaction(self, cp_id, connector_id, id_tag, meter_start):
        from .models_ocpp import ChargingStation, ChargingSession, ChargingRfidTag
        import random
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        tx_id = random.randint(100000, 999999)
        if not station:
            return tx_id

        user = None
        tag = ChargingRfidTag.objects.filter(home=station.home, id_tag=id_tag).first()
        if tag and tag.user:
            user = tag.user
        elif station.home and station.home.user:
            user = station.home.user

        session = ChargingSession.objects.create(
            station=station,
            transaction_id=tx_id,
            id_tag=id_tag,
            user=user,
            start_time=timezone.now(),
            meter_start_wh=float(meter_start),
            status="active"
        )
        station.active_transaction_id = tx_id
        station.status = "Charging"
        station.session_energy_kwh = 0.0
        station.save(update_fields=["active_transaction_id", "status", "session_energy_kwh"])
        return tx_id

    @database_sync_to_async
    def finish_stop_transaction(self, cp_id, tx_id, meter_stop, reason, id_tag):
        from .models_ocpp import ChargingStation, ChargingSession
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return

        session = None
        if tx_id:
            session = ChargingSession.objects.filter(station=station, transaction_id=tx_id).first()
        if not session:
            session = ChargingSession.objects.filter(station=station, status="active").first()

        if session:
            session.stop_time = timezone.now()
            session.meter_stop_wh = float(meter_stop)
            session.total_energy_kwh = max(0.0, round((session.meter_stop_wh - session.meter_start_wh) / 1000.0, 2))
            session.stop_reason = reason
            session.status = "completed"
            
            # Solare Deckungsquote berechnen
            # Falls Smart Charging aktiv war, 80-100% PV-Anteil annehmen
            if station.smart_charging_mode == "pv_surplus":
                session.solar_coverage_pct = 95.0
                session.solar_energy_kwh = round(session.total_energy_kwh * 0.95, 2)
                session.grid_energy_kwh = round(session.total_energy_kwh * 0.05, 2)
            else:
                session.solar_coverage_pct = 50.0
                session.solar_energy_kwh = round(session.total_energy_kwh * 0.5, 2)
                session.grid_energy_kwh = round(session.total_energy_kwh * 0.5, 2)
                
            # Kosten berechnen (z. B. 0.28 EUR/kWh Netzstrom, 0.08 EUR/kWh Solarstrom)
            cost = (Decimal(str(session.grid_energy_kwh)) * Decimal("0.28")) + (Decimal(str(session.solar_energy_kwh)) * Decimal("0.08"))
            session.cost_eur = round(cost, 2)
            session.save()

        station.active_transaction_id = None
        station.status = "Available"
        station.active_power_w = 0.0
        station.current_l1 = 0.0
        station.current_l2 = 0.0
        station.current_l3 = 0.0
        station.save(update_fields=["active_transaction_id", "status", "active_power_w", "current_l1", "current_l2", "current_l3"])

    @database_sync_to_async
    def update_target_current(self, cp_id, current_a):
        from .models_ocpp import ChargingStation
        ChargingStation.objects.filter(charge_point_id=cp_id).update(target_current_a=current_a)

    async def broadcast_wallbox_update(self):
        """Sendet Live-Wallbox-Status an alle verbundenen Web-Clients im Haushalt."""
        if not self.home_group:
            return
        try:
            await self.channel_layer.group_send(
                self.home_group,
                {
                    "type": "wallbox_update",
                    "charge_point_id": self.cp_id
                }
            )
        except Exception as e:
            logger.debug(f"Wallbox broadcast failed: {e}")
