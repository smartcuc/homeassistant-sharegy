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
    OCPP 1.6-J, OCPP 2.0.1 & OCPP 2.1 JSON over WebSocket CSMS Gateway.
    Verbindet Wallboxen (Easee, go-e, Keba, Alfen, Mennekes, Zaptec, etc.)
    direkt mit der Sharegy Cloud für intelligentes PV-Überschuss-, Börsenstrom-
    und V2G/V2H-Bidirektionales Laden (ISO 15118-20).
    """

    async def connect(self):
        self.cp_id = self.scope["url_route"]["kwargs"].get("cp_id", "default_cp").strip()
        self.group_name = f"ocpp_{self.cp_id}"
        self.home_group = None

        # OCPP Subprotocol aushandeln (Priorität: OCPP 2.1 > OCPP 2.0.1 > OCPP 1.6)
        subprotocols = self.scope.get("subprotocols", [])
        selected_subprotocol = "ocpp1.6"
        if "ocpp2.1" in subprotocols:
            selected_subprotocol = "ocpp2.1"
        elif "ocpp2.0.1" in subprotocols:
            selected_subprotocol = "ocpp2.0.1"
        elif "ocpp1.6" in subprotocols:
            selected_subprotocol = "ocpp1.6"

        self.ocpp_version = selected_subprotocol
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept(subprotocol=selected_subprotocol)

        # Station in DB online setzen und Protokollversion speichern
        station_info = await self.get_or_create_station(self.cp_id, selected_subprotocol)
        if station_info and station_info.get("home_id"):
            self.home_group = f"home_{station_info['home_id']}"
            await self.channel_layer.group_add(self.home_group, self.channel_name)

        logger.info(f"⚡ OCPP-Wallbox verbunden: {self.cp_id} (Protokoll: {selected_subprotocol})")

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
                await self.handle_ocpp_call_result(unique_id, payload)

            elif msg_type == CALLERROR:
                error_code = msg[2]
                error_desc = msg[3] if len(msg) > 3 else ""
                logger.warning(f"OCPP CallError von {self.cp_id} für {unique_id}: [{error_code}] {error_desc}")

        except Exception as e:
            logger.error(f"Fehler bei OCPP Nachricht von {self.cp_id}: {e}", exc_info=True)

    async def handle_ocpp_call(self, unique_id: str, action: str, payload: dict):
        """Verarbeitet eingehende OCPP 1.6-J, 2.0.1 und 2.1 Aufrufe der Wallbox."""
        now_iso = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if action == "BootNotification":
            # Unterstützt sowohl OCPP 1.6 als auch OCPP 2.0.1 / 2.1 Datenformate
            if "chargingStation" in payload:
                cs = payload.get("chargingStation", {})
                vendor = cs.get("vendorName", "")
                model = cs.get("model", "")
                serial = cs.get("serialNumber", "")
                fw = cs.get("firmwareVersion", "")
            else:
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
            # Unterstützt OCPP 1.6 (`status`) & OCPP 2.0.1/2.1 (`connectorStatus`)
            connector_id = payload.get("connectorId", 1)
            status = payload.get("status") or payload.get("connectorStatus", "Available")
            if status == "Occupied":
                status = "Preparing"
            error_code = payload.get("errorCode", "NoError")
            await self.update_status(self.cp_id, connector_id, status, error_code)

            res = {}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "MeterValues":
            connector_id = payload.get("connectorId") or payload.get("evseId", 1)
            tx_id = payload.get("transactionId")
            meter_values = payload.get("meterValue", [])
            await self.process_meter_values(self.cp_id, connector_id, tx_id, meter_values)

            res = {}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "Authorize":
            # Unterstützt OCPP 1.6 `idTag` und OCPP 2.0.1/2.1 `idToken`
            id_tag = ""
            if "idToken" in payload:
                id_token_data = payload.get("idToken")
                id_tag = id_token_data.get("idToken", "") if isinstance(id_token_data, dict) else str(id_token_data)
            else:
                id_tag = payload.get("idTag", "")

            auth_status = await self.validate_rfid_tag(self.cp_id, id_tag)
            expiry_iso = (timezone.now() + timezone.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            # Antwort-Format nach OCPP Version
            if self.ocpp_version in ["ocpp2.0.1", "ocpp2.1"]:
                res = {
                    "idTokenInfo": {
                        "status": auth_status,
                        "cacheExpiryDateTime": expiry_iso
                    }
                }
            else:
                res = {
                    "idTagInfo": {
                        "status": auth_status,
                        "expiryDate": expiry_iso
                    }
                }
            await self.send_call_result(unique_id, res)

        elif action == "StartTransaction":
            # OCPP 1.6 StartTransaction
            connector_id = payload.get("connectorId", 1)
            id_tag = payload.get("idTag", "")
            meter_start = payload.get("meterStart", 0)
            tx_id, auth_status = await self.create_start_transaction(self.cp_id, connector_id, id_tag, meter_start)

            res = {
                "transactionId": tx_id or 0,
                "idTagInfo": {"status": auth_status}
            }
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "StopTransaction":
            # OCPP 1.6 StopTransaction
            tx_id = payload.get("transactionId")
            meter_stop = payload.get("meterStop", 0)
            reason = payload.get("reason", "Local")
            id_tag = payload.get("idTag", "")
            await self.finish_stop_transaction(self.cp_id, tx_id, meter_stop, reason, id_tag)

            res = {"idTagInfo": {"status": "Accepted"}}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        # ============================================================
        # 🚗 OCPP 2.0.1 & OCPP 2.1 TRANSACTION EVENT (ISO 15118 / V2G)
        # ============================================================
        elif action == "TransactionEvent":
            event_type = payload.get("eventType", "Updated")  # Started, Updated, Ended
            tx_info = payload.get("transactionInfo", {})
            raw_tx_id = tx_info.get("transactionId", 0)
            try:
                tx_id = int(str(raw_tx_id).replace("-", "")[:8])
            except (ValueError, TypeError):
                tx_id = 100001

            id_token_data = payload.get("idToken") or {}
            id_tag = id_token_data.get("idToken", "") if isinstance(id_token_data, dict) else str(id_token_data)
            evse = payload.get("evse") or {}
            connector_id = evse.get("connectorId", 1)
            meter_values = payload.get("meterValue", [])
            stopped_reason = tx_info.get("stoppedReason", "Local")

            if event_type == "Started":
                meter_start = 0
                if meter_values and len(meter_values) > 0:
                    for sv in meter_values[0].get("sampledValue", []):
                        if "Energy.Active.Import" in sv.get("measurand", "Energy.Active.Import.Register"):
                            try:
                                meter_start = float(sv.get("value", 0))
                            except ValueError:
                                pass
                await self.create_start_transaction(self.cp_id, connector_id, id_tag, meter_start, custom_tx_id=tx_id)

            elif event_type == "Updated":
                if meter_values:
                    await self.process_meter_values(self.cp_id, connector_id, tx_id, meter_values)

            elif event_type == "Ended":
                meter_stop = 0
                if meter_values and len(meter_values) > 0:
                    for sv in meter_values[-1].get("sampledValue", []):
                        if "Energy.Active.Import" in sv.get("measurand", "Energy.Active.Import.Register"):
                            try:
                                meter_stop = float(sv.get("value", 0))
                            except ValueError:
                                pass
                await self.finish_stop_transaction(self.cp_id, tx_id, meter_stop, stopped_reason, id_tag)

            res = {"idTokenInfo": {"status": "Accepted"}} if event_type in ["Started", "Updated"] else {}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        # ============================================================
        # 📋 OCPP 2.0.1 & 2.1 DEVICE MODEL & MONITORING (NotifyEvent)
        # ============================================================
        elif action == "NotifyEvent":
            event_data = payload.get("eventData", [])
            await self.save_device_variables(self.cp_id, event_data)
            res = {}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        # ============================================================
        # 🔐 ISO 15118-2 / ISO 15118-20 PLUG & CHARGE CERTIFICATE
        # ============================================================
        elif action == "Get15118EVCertificate":
            schema_ver = payload.get("iso15118SchemaVersion", "urn:iso:15118:20:CommonMessages")
            res = {
                "status": "Accepted",
                "exiResponse": "00"
            }
            await self.send_call_result(unique_id, res)
            logger.info(f"🔐 ISO 15118-20 Certificate angefordert für {self.cp_id} (Schema: {schema_ver})")

        elif action == "DiagnosticsStatusNotification":
            diag_status = payload.get("status", "Idle")
            await self.update_diagnostics_status(self.cp_id, diag_status)
            res = {}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "FirmwareStatusNotification":
            res = {}
            await self.send_call_result(unique_id, res)
            await self.broadcast_wallbox_update()

        elif action == "DataTransfer":
            res = {"status": "Accepted"}
            await self.send_call_result(unique_id, res)

        else:
            logger.info(f"Unbehandelte OCPP Action '{action}' von {self.cp_id}")
            res = {}
            await self.send_call_result(unique_id, res)

    async def handle_ocpp_call_result(self, unique_id: str, payload: dict):
        """Verarbeitet Antworten der Wallbox auf von Sharegy gesendete Anfragen."""
        if not isinstance(payload, dict):
            return

        # 1. GetCompositeSchedule Antwort
        if "chargingSchedule" in payload or "scheduleStart" in payload:
            await self.save_composite_schedule(self.cp_id, payload)
            await self.broadcast_wallbox_update()
            logger.info(f"📊 Composite Schedule für {self.cp_id} gespeichert.")

        # 2. GetLocalListVersion Antwort
        if "listVersion" in payload:
            list_version = int(payload.get("listVersion", 0))
            await self.update_local_list_version(self.cp_id, list_version)
            await self.broadcast_wallbox_update()
            logger.info(f"💳 LocalListVersion für {self.cp_id}: {list_version}")

        # 3. GetDiagnostics Antwort
        if "fileName" in payload:
            file_name = str(payload.get("fileName", ""))
            await self.save_diagnostics_file_name(self.cp_id, file_name)
            await self.broadcast_wallbox_update()

        # 4. GetVariables Antwort (OCPP 2.0.1 / 2.1)
        if "getVariableResult" in payload:
            await self.save_get_variables_result(self.cp_id, payload.get("getVariableResult", []))
            await self.broadcast_wallbox_update()

    async def send_call_result(self, unique_id: str, payload: dict):
        """Sendet ein OCPP CALLRESULT [3, unique_id, payload]."""
        msg = [CALLRESULT, unique_id, payload]
        await self.send(text_data=json.dumps(msg))

    async def send_call(self, action: str, payload: dict):
        """Sendet einen OCPP CALL [2, unique_id, action, payload] an die Wallbox."""
        unique_id = str(uuid.uuid4())
        msg = [CALL, unique_id, action, payload]
        await self.send(text_data=json.dumps(msg))
        return unique_id

    # ============================================================
    # 📡 CHANNEL LAYER HANDLER (VON REST-API ODER SMART CHARGER)
    # ============================================================

    async def ocpp_set_v2g_profile(self, event):
        """
        Setzt ein bidirektionales V2G/V2H Lade- oder Entladeprofil
        (Negative Leistung = Entladen ins Haus/Netz, Positive Leistung = Laden).
        """
        power_w = float(event.get("power_w", 0.0))
        current_a = float(event.get("current_a", 0.0))
        connector_id = int(event.get("connector_id", 1))

        if self.ocpp_version in ["ocpp2.0.1", "ocpp2.1"]:
            # OCPP 2.0.1 & 2.1 SetChargingProfile mit Watt
            payload = {
                "evseId": connector_id,
                "chargingProfile": {
                    "id": 1,
                    "stackLevel": 1,
                    "chargingProfilePurpose": "TxDefaultProfile",
                    "chargingProfileKind": "Relative",
                    "chargingSchedule": [
                        {
                            "id": 1,
                            "startSchedule": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "duration": 86400,
                            "chargingRateUnit": "W",
                            "chargingSchedulePeriod": [
                                {
                                    "startPeriod": 0,
                                    "limit": power_w,
                                    "numberPhases": 3
                                }
                            ]
                        }
                    ]
                }
            }
        else:
            # OCPP 1.6 SetChargingProfile mit Ampere
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
                                "limit": abs(current_a),
                                "numberPhases": 3
                            }
                        ]
                    }
                }
            }

        await self.send_call("SetChargingProfile", payload)
        logger.info(f"🔄 OCPP V2G Profile gesendet an {self.cp_id}: {power_w:.0f} W / {current_a} A")

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

    async def ocpp_clear_charging_profile(self, event):
        """Löscht das aktive Ladeprofil (Wallbox lädt mit Default-Einstellung oder stoppt)."""
        payload = {
            "id": int(event.get("charging_profile_id", 1)),
            "connectorId": int(event.get("connector_id", 1)),
        }
        await self.send_call("ClearChargingProfile", payload)
        await self.update_target_current(self.cp_id, 0.0)
        logger.info(f"🧹 ClearChargingProfile an {self.cp_id}")

    async def ocpp_get_composite_schedule(self, event):
        """Fragt den effektiven zusammengesetzten Ladefahrplan der Wallbox ab."""
        connector_id = int(event.get("connector_id", 1))
        duration = int(event.get("duration", 86400))
        rate_unit = event.get("charging_rate_unit", "A")
        payload = {
            "connectorId": connector_id,
            "duration": duration,
            "chargingRateUnit": rate_unit
        }
        await self.send_call("GetCompositeSchedule", payload)
        logger.info(f"📊 GetCompositeSchedule an {self.cp_id} (Duration: {duration}s)")

    async def ocpp_trigger_message(self, event):
        """Fordert die Wallbox auf, eine bestimmte Nachricht sofort zu senden (Remote Trigger)."""
        requested_message = event.get("requested_message", "StatusNotification")
        connector_id = event.get("connector_id")
        if self.ocpp_version in ["ocpp2.0.1", "ocpp2.1"]:
            payload = {"requestedMessage": requested_message}
            if connector_id is not None:
                payload["evse"] = {"id": int(connector_id)}
        else:
            payload = {"requestedMessage": requested_message}
            if connector_id is not None:
                payload["connectorId"] = int(connector_id)
        await self.send_call("TriggerMessage", payload)
        logger.info(f"🎯 TriggerMessage an {self.cp_id}: {requested_message}")

    async def ocpp_send_local_list(self, event):
        """Sendet die RFID-Berechtigungsliste an die Wallbox (OCPP Local Auth List)."""
        list_version = int(event.get("list_version", 1))
        update_type = event.get("update_type", "Full")
        local_auth_list = event.get("local_authorization_list", [])
        payload = {
            "listVersion": list_version,
            "updateType": update_type,
            "localAuthorizationList": local_auth_list
        }
        await self.send_call("SendLocalList", payload)
        await self.update_local_list_version(self.cp_id, list_version)
        await self.broadcast_wallbox_update()
        logger.info(f"💳 SendLocalList an {self.cp_id}: Version {list_version} ({len(local_auth_list)} Einträge)")

    async def ocpp_get_local_list_version(self, event):
        """Fragt die aktuelle Versionsnummer der lokalen Auth-Liste auf der Box ab."""
        payload = {}
        await self.send_call("GetLocalListVersion", payload)
        logger.info(f"💳 GetLocalListVersion an {self.cp_id}")

    async def ocpp_get_diagnostics(self, event):
        """Fordert die Wallbox auf, Diagnosedaten an einen Ziel-Server hochzuladen."""
        location = event.get("location", "https://sharegy.de/api/energy/wallboxes/diagnostics-upload/")
        start_time = event.get("start_time")
        stop_time = event.get("stop_time")
        retries = int(event.get("retries", 3))
        retry_interval = int(event.get("retry_interval", 30))

        payload = {
            "location": location,
            "retries": retries,
            "retryInterval": retry_interval,
        }
        if start_time:
            payload["startTime"] = start_time
        if stop_time:
            payload["stopTime"] = stop_time

        await self.send_call("GetDiagnostics", payload)
        await self.update_diagnostics_status(self.cp_id, "Uploading")
        await self.broadcast_wallbox_update()
        logger.info(f"🛠️ GetDiagnostics an {self.cp_id} (Location: {location})")

    async def ocpp_get_variables(self, event):
        """Liest Device-Model-Variablen ab (OCPP 2.0.1 / 2.1 GetVariables)."""
        get_variable_data = event.get("get_variable_data", [])
        payload = {"getVariableData": get_variable_data}
        await self.send_call("GetVariables", payload)
        logger.info(f"🔍 GetVariables an {self.cp_id}")

    async def ocpp_set_variables(self, event):
        """Schreibt Device-Model-Variablen (OCPP 2.0.1 / 2.1 SetVariables)."""
        set_variable_data = event.get("set_variable_data", [])
        payload = {"setVariableData": set_variable_data}
        await self.send_call("SetVariables", payload)
        logger.info(f"✏️ SetVariables an {self.cp_id}")

    async def ocpp_remote_start(self, event):
        """Startet den Ladevorgang aus der Sharegy App heraus."""
        connector_id = int(event.get("connector_id", 1))
        id_tag = event.get("id_tag", "SHAREGY_APP")
        if self.ocpp_version in ["ocpp2.0.1", "ocpp2.1"]:
            payload = {
                "evseId": connector_id,
                "remoteStartId": 1,
                "idToken": {
                    "idToken": id_tag,
                    "type": "ISO14443"
                }
            }
            await self.send_call("RequestStartTransaction", payload)
            logger.info(f"▶️ RequestStartTransaction (OCPP 2.x) an {self.cp_id} (Tag: {id_tag})")
        else:
            payload = {
                "connectorId": connector_id,
                "idTag": id_tag
            }
            await self.send_call("RemoteStartTransaction", payload)
            logger.info(f"▶️ RemoteStartTransaction an {self.cp_id} (Tag: {id_tag})")

    async def ocpp_remote_stop(self, event):
        """Stoppt die aktive Ladesitzung."""
        tx_id = event.get("transaction_id")
        if not tx_id:
            tx_id = await self.get_active_or_latest_transaction_id(self.cp_id)
        if tx_id:
            if self.ocpp_version in ["ocpp2.0.1", "ocpp2.1"]:
                payload = {"transactionId": str(tx_id)}
                await self.send_call("RequestStopTransaction", payload)
                logger.info(f"⏹️ RequestStopTransaction (OCPP 2.x) an {self.cp_id} (Tx: {tx_id})")
            else:
                payload = {"transactionId": int(tx_id)}
                await self.send_call("RemoteStopTransaction", payload)
                logger.info(f"⏹️ RemoteStopTransaction an {self.cp_id} (Tx: {tx_id})")

    async def ocpp_unlock_connector(self, event):
        """Entriegelt das Ladekabel."""
        connector_id = int(event.get("connector_id", 1))
        if self.ocpp_version in ["ocpp2.0.1", "ocpp2.1"]:
            payload = {"evseId": 1, "connectorId": connector_id}
        else:
            payload = {"connectorId": connector_id}
        await self.send_call("UnlockConnector", payload)
        logger.info(f"🔓 UnlockConnector an {self.cp_id} (Connector: {connector_id})")

    async def ocpp_reserve_now(self, event):
        """Reserviert die Ladesäule für einen bestimmten RFID-Tag / Nutzer (OCPP 1.6 & 2.x ReserveNow)."""
        connector_id = int(event.get("connector_id", 1))
        id_tag = event.get("id_tag", "RESERVED_USER")
        reservation_id = int(event.get("reservation_id", 1))
        expiry_iso = event.get("expiry_date") or (timezone.now() + timezone.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if self.ocpp_version in ["ocpp2.0.1", "ocpp2.1"]:
            payload = {
                "id": reservation_id,
                "expiryDateTime": expiry_iso,
                "idToken": {"idToken": id_tag, "type": "ISO14443"},
                "evseId": connector_id,
            }
        else:
            payload = {
                "connectorId": connector_id,
                "expiryDate": expiry_iso,
                "idTag": id_tag,
                "reservationId": reservation_id,
            }
        await self.send_call("ReserveNow", payload)
        await self.set_station_reserved(self.cp_id, reservation_id, id_tag, expiry_iso)
        await self.broadcast_wallbox_update()
        logger.info(f"🔒 ReserveNow an {self.cp_id} (ResId: {reservation_id}, Tag: {id_tag})")

    async def ocpp_cancel_reservation(self, event):
        """Hebt eine bestehende Reservierung auf (OCPP 1.6 & 2.x CancelReservation)."""
        reservation_id = int(event.get("reservation_id", 1))
        payload = {"reservationId": reservation_id}
        await self.send_call("CancelReservation", payload)
        await self.clear_station_reservation(self.cp_id)
        await self.broadcast_wallbox_update()
        logger.info(f"🔓 CancelReservation an {self.cp_id} (ResId: {reservation_id})")

    async def ocpp_change_availability(self, event):
        """Ändert Verfügbarkeit (Operative / Inoperative)."""
        connector_id = int(event.get("connector_id", 1))
        avail_type = event.get("type", "Operative")
        payload = {
            "connectorId": connector_id,
            "type": avail_type
        }
        await self.send_call("ChangeAvailability", payload)
        await self.set_station_availability(self.cp_id, avail_type)
        await self.broadcast_wallbox_update()
        logger.info(f"⚙️ ChangeAvailability an {self.cp_id}: {avail_type}")

    async def ocpp_reset(self, event):
        """Führt einen Soft- oder Hard-Reset der Wallbox durch."""
        reset_type = event.get("type", "Soft")
        if self.ocpp_version in ["ocpp2.0.1", "ocpp2.1"]:
            reset_val = "Immediate" if str(reset_type).lower() == "hard" else "OnIdle"
            payload = {"type": reset_val}
        else:
            payload = {"type": reset_type}
        await self.send_call("Reset", payload)
        logger.info(f"🔄 Reset an {self.cp_id}: {reset_type}")

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
    def get_or_create_station(self, cp_id: str, ocpp_ver: str = "ocpp1.6"):
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
                ocpp_version=ocpp_ver,
                is_online=True,
                last_heartbeat=timezone.now()
            )
        else:
            station.is_online = True
            station.ocpp_version = ocpp_ver
            station.last_heartbeat = timezone.now()
            station.save(update_fields=["is_online", "ocpp_version", "last_heartbeat"])
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
            # Wenn Station nicht aktiv lädt oder blockiert/reserviert ist, Live-Leistung nullen
            if status in ["Available", "Faulted", "Unavailable", "Reserved"]:
                station.active_power_w = 0.0
                station.v2g_discharge_power_w = 0.0
                station.current_l1 = 0.0
                station.current_l2 = 0.0
                station.current_l3 = 0.0
                station.target_current_a = 0.0
                if status in ["Available", "Unavailable", "Faulted"]:
                    station.active_transaction_id = None
            station.save(update_fields=[
                "status", "error_code", "is_online", "last_heartbeat",
                "active_power_w", "v2g_discharge_power_w", "current_l1", "current_l2", "current_l3",
                "target_current_a", "active_transaction_id"
            ])

    @database_sync_to_async
    def process_meter_values(self, cp_id, connector_id, tx_id, meter_values):
        from .models_ocpp import ChargingStation, ChargingSession
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return

        power_import_w = 0.0
        power_export_w = 0.0
        current_l1 = 0.0
        current_l2 = 0.0
        current_l3 = 0.0
        voltage_v = 230.0
        energy_import_wh = None
        energy_export_wh = None
        ev_soc = None

        for mv in meter_values:
            sampled_values = mv.get("sampledValue", [])
            for sv in sampled_values:
                measurand = sv.get("measurand", "Energy.Active.Import.Register")
                val_str = sv.get("value", "0")
                phase = sv.get("phase")
                unit = sv.get("unit", "")
                if isinstance(sv.get("unitOfMeasure"), dict):
                    unit = sv.get("unitOfMeasure", {}).get("unit", unit)
                elif sv.get("unitOfMeasure"):
                    unit = str(sv.get("unitOfMeasure"))
                try:
                    val = float(val_str)
                except ValueError:
                    continue

                if measurand == "Power.Active.Import":
                    power_import_w = val * 1000.0 if unit.lower() in ["kw", "kvar"] else val
                elif measurand == "Power.Active.Export":
                    # 🚗 V2G / V2H Entladeleistung
                    power_export_w = val * 1000.0 if unit.lower() in ["kw", "kvar"] else val
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
                    energy_import_wh = val * 1000.0 if unit.lower() in ["kwh", "kvarh"] else val
                elif measurand in ["Energy.Active.Export.Register", "Energy.Active.Export.Interval"]:
                    energy_export_wh = val * 1000.0 if unit.lower() in ["kwh", "kvarh"] else val
                elif measurand in ["SoC", "StateOfCharge"]:
                    # 🔋 ISO 15118-20 Fahrzeug-Ladestand
                    ev_soc = val

        station.active_power_w = power_import_w
        station.v2g_discharge_power_w = power_export_w
        station.current_l1 = current_l1
        station.current_l2 = current_l2
        station.current_l3 = current_l3
        station.voltage_v = voltage_v

        if ev_soc is not None:
            station.ev_soc_pct = ev_soc

        # Status Update
        if power_import_w > 50.0:
            if station.status not in ["Reserved", "Unavailable", "Faulted", "SuspendedEVSE"]:
                station.status = "Charging"
        elif power_export_w > 50.0:
            # V2G / V2H Entladung
            station.status = "Charging"
        elif station.status == "Charging" and power_import_w <= 10.0 and power_export_w <= 10.0 and station.active_transaction_id:
            station.status = "SuspendedEV"

        if energy_import_wh is not None:
            station.total_energy_kwh = round(energy_import_wh / 1000.0, 3)

        # Aktive Session aktualisieren
        if tx_id:
            session = ChargingSession.objects.filter(station=station, transaction_id=tx_id, status="active").first()
            if session:
                if energy_import_wh is not None:
                    session_kwh = max(0.0, (energy_import_wh - session.meter_start_wh) / 1000.0)
                    session.total_energy_kwh = round(session_kwh, 2)
                    station.session_energy_kwh = session.total_energy_kwh
                    session.save(update_fields=["total_energy_kwh"])
                if energy_export_wh is not None:
                    session.v2g_discharged_kwh = round(energy_export_wh / 1000.0, 2)
                    session.save(update_fields=["v2g_discharged_kwh"])

        station.last_heartbeat = timezone.now()
        station.save(update_fields=[
            "active_power_w", "v2g_discharge_power_w", "current_l1", "current_l2", "current_l3",
            "voltage_v", "status", "total_energy_kwh", "session_energy_kwh", "ev_soc_pct", "last_heartbeat"
        ])

    @database_sync_to_async
    def validate_rfid_tag(self, cp_id, id_tag):
        from .models_ocpp import ChargingRfidTag, ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return "Accepted"
        if station.status in ["Unavailable", "Faulted"]:
            return "Blocked"
        tags_count = ChargingRfidTag.objects.filter(home=station.home).count()
        if tags_count == 0:
            return "Accepted"
        tag = ChargingRfidTag.objects.filter(home=station.home, id_tag=id_tag, is_active=True).first()
        return "Accepted" if tag else "Invalid"

    @database_sync_to_async
    def create_start_transaction(self, cp_id, connector_id, id_tag, meter_start, custom_tx_id=None):
        from .models_ocpp import ChargingStation, ChargingSession, ChargingRfidTag
        import random
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return 0, "Invalid"

        # 1. Wenn Station im Fehler- oder Nicht-Verfügbar-Zustand ist
        if station.status in ["Unavailable", "Faulted"]:
            logger.warning(f"🚫 StartTransaction abgelehnt für {cp_id}: Status ist {station.status}")
            return 0, "Blocked"

        # 2. Wenn Station Reserviert ist: Nur autorisierten Reservierungs-Inhaber zulassen
        if station.status == "Reserved":
            if station.reserved_id_tag and station.reserved_id_tag != id_tag:
                logger.warning(f"🚫 StartTransaction abgelehnt für {cp_id}: Station ist reserviert für '{station.reserved_id_tag}', Anfrage kam von '{id_tag}'")
                return 0, "Blocked"
            # Reservierung auflösen, da berechtigter Ladevorgang startet
            station.reserved_id_tag = ""
            station.reservation_id = None
            station.reservation_expiry = None

        # 3. RFID Autorisierung prüfen
        tags_count = ChargingRfidTag.objects.filter(home=station.home).count()
        user = None
        if tags_count > 0:
            tag = ChargingRfidTag.objects.filter(home=station.home, id_tag=id_tag, is_active=True).first()
            if not tag:
                logger.warning(f"🚫 StartTransaction abgelehnt für {cp_id}: Unbekannter RFID Tag '{id_tag}'")
                return 0, "Invalid"
            user = tag.user
        elif station.home and station.home.user:
            user = station.home.user

        tx_id = custom_tx_id or random.randint(100000, 999999)
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
        station.save(update_fields=[
            "active_transaction_id", "status", "session_energy_kwh",
            "reserved_id_tag", "reservation_id", "reservation_expiry"
        ])
        return tx_id, "Accepted"

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
            if station.smart_charging_mode == "pv_surplus":
                session.solar_coverage_pct = 95.0
                session.solar_energy_kwh = round(session.total_energy_kwh * 0.95, 2)
                session.grid_energy_kwh = round(session.total_energy_kwh * 0.05, 2)
            else:
                session.solar_coverage_pct = 50.0
                session.solar_energy_kwh = round(session.total_energy_kwh * 0.5, 2)
                session.grid_energy_kwh = round(session.total_energy_kwh * 0.5, 2)
                
            cost = (Decimal(str(session.grid_energy_kwh)) * Decimal("0.28")) + (Decimal(str(session.solar_energy_kwh)) * Decimal("0.08"))
            session.cost_eur = round(cost, 2)
            session.save()

        station.active_transaction_id = None
        station.status = "Available"
        station.active_power_w = 0.0
        station.current_l1 = 0.0
        station.current_l2 = 0.0
        station.current_l3 = 0.0
        station.target_current_a = 0.0
        station.save(update_fields=[
            "active_transaction_id", "status", "active_power_w",
            "current_l1", "current_l2", "current_l3", "target_current_a"
        ])

    @database_sync_to_async
    def get_active_or_latest_transaction_id(self, cp_id):
        from .models_ocpp import ChargingStation, ChargingSession
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return 0
        if station.active_transaction_id:
            return station.active_transaction_id
        active_sess = ChargingSession.objects.filter(station=station, status="active").order_by("-start_time").first()
        return active_sess.transaction_id if active_sess else 0

    @database_sync_to_async
    def set_station_reserved(self, cp_id, reservation_id, id_tag, expiry_iso):
        from .models_ocpp import ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if station:
            station.status = "Reserved"
            station.reservation_id = reservation_id
            station.reserved_id_tag = id_tag
            station.active_power_w = 0.0
            station.target_current_a = 0.0
            station.save(update_fields=["status", "reservation_id", "reserved_id_tag", "active_power_w", "target_current_a"])

    @database_sync_to_async
    def clear_station_reservation(self, cp_id):
        from .models_ocpp import ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if station:
            station.status = "Available"
            station.reservation_id = None
            station.reserved_id_tag = ""
            station.reservation_expiry = None
            station.save(update_fields=["status", "reservation_id", "reserved_id_tag", "reservation_expiry"])

    @database_sync_to_async
    def set_station_availability(self, cp_id, avail_type):
        from .models_ocpp import ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if station:
            station.status = "Available" if avail_type == "Operative" else "Unavailable"
            if station.status == "Unavailable":
                station.active_power_w = 0.0
                station.target_current_a = 0.0
            station.save(update_fields=["status", "active_power_w", "target_current_a"])

    @database_sync_to_async
    def update_target_current(self, cp_id, current_a):
        from .models_ocpp import ChargingStation
        ChargingStation.objects.filter(charge_point_id=cp_id).update(target_current_a=current_a)

    @database_sync_to_async
    def update_diagnostics_status(self, cp_id, status_str):
        from .models_ocpp import ChargingStation
        ChargingStation.objects.filter(charge_point_id=cp_id).update(diagnostics_status=status_str)

    @database_sync_to_async
    def save_diagnostics_file_name(self, cp_id, file_name):
        from .models_ocpp import ChargingStation
        ChargingStation.objects.filter(charge_point_id=cp_id).update(last_diagnostics_file=file_name)

    @database_sync_to_async
    def update_local_list_version(self, cp_id, version_num):
        from .models_ocpp import ChargingStation
        ChargingStation.objects.filter(charge_point_id=cp_id).update(local_auth_list_version=version_num)

    @database_sync_to_async
    def save_composite_schedule(self, cp_id, schedule_data):
        from .models_ocpp import ChargingStation
        ChargingStation.objects.filter(charge_point_id=cp_id).update(composite_schedule_data=schedule_data)

    @database_sync_to_async
    def save_device_variables(self, cp_id, event_data_list):
        from .models_ocpp import ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return
        current_vars = station.device_variables or {}
        for ev in event_data_list:
            comp = ev.get("component", {}).get("name", "Unknown")
            var = ev.get("variable", {}).get("name", "Unknown")
            val = ev.get("actualValue")
            key = f"{comp}.{var}"
            current_vars[key] = {
                "value": val,
                "timestamp": ev.get("timestamp", timezone.now().isoformat()),
                "trigger": ev.get("trigger", "Periodic")
            }
        station.device_variables = current_vars
        station.save(update_fields=["device_variables"])

    @database_sync_to_async
    def save_get_variables_result(self, cp_id, get_var_results):
        from .models_ocpp import ChargingStation
        station = ChargingStation.objects.filter(charge_point_id=cp_id).first()
        if not station:
            return
        current_vars = station.device_variables or {}
        for item in get_var_results:
            comp = item.get("component", {}).get("name", "Unknown")
            var = item.get("variable", {}).get("name", "Unknown")
            val = item.get("attributeValue")
            status = item.get("attributeStatus", "Accepted")
            if status == "Accepted":
                key = f"{comp}.{var}"
                current_vars[key] = {
                    "value": val,
                    "timestamp": timezone.now().isoformat()
                }
        station.device_variables = current_vars
        station.save(update_fields=["device_variables"])

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
