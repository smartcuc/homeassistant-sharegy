######################
# devices/consumers.py
######################

import json
import logging
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.db import close_old_connections

from devices.models import Home, Device
from devices.services.ingest import ingest_metric_payload

logger = logging.getLogger(__name__)


@database_sync_to_async
def process_incoming_telemetry(token, payload_str, user):
    """
    Verarbeitet eingehende Telemetrie-Daten über WebSocket
    (Shelly Outbound WebSocket RPC, Tasmota, ioBroker, direkte JSON-Frames).
    """
    close_old_connections()
    try:
        try:
            data = json.loads(payload_str)
        except Exception:
            logger.warning("[WS-Ingest] Ungültiges JSON empfangen: %s", payload_str[:100])
            return None

        # 1. Home ermitteln (über Token oder authentifizierten User)
        home = None
        if token:
            home = Home.objects.filter(mqtt_token=token).select_related("user").first()

        if not home and user and user.is_authenticated:
            home = Home.objects.filter(user=user).first()

        if not home:
            # Fallback: Versuche Token aus dem JSON-Payload zu lesen
            payload_token = data.get("token") or data.get("home_token")
            if payload_token:
                home = Home.objects.filter(mqtt_token=payload_token).select_related("user").first()

        if not home:
            logger.warning("[WS-Ingest] Kein Haushalt gefunden für Token='%s' / User='%s'", token, user)
            return None

        # 2. Device Identifier ermitteln (z. B. "shellyplus1pm-xxx", "shellypro3em-yyy")
        raw_src = data.get("src") or data.get("device_id") or data.get("identifier") or data.get("id") or "ws_device"
        identifier = str(raw_src).strip()

        # 3. Device abrufen oder per Auto-Discovery anlegen
        device, created = Device.objects.get_or_create(
            home=home,
            identifier=identifier,
            defaults={
                "name": identifier,
                "configured": True,
                "active": True,
            },
        )
        if created:
            logger.info("[WS-Ingest] Neues Gerät per WebSocket entdeckt: %s (Home: %s)", identifier, home.name)

        # 4. Metriken extrahieren (Shelly RPC NotifyStatus, NotifyEvent oder flaches JSON)
        metrics = {}
        meta = {"from": "websocket", "src": identifier}

        params = data.get("params", {}) if isinstance(data.get("params"), dict) else data

        # A) Shelly 3EM / Pro 3EM (em:0, emdata:0)
        if "em:0" in params:
            em0 = params.get("em:0", {})
            if "total_act_power" in em0:
                metrics["power"] = float(em0["total_act_power"])
            elif "a_act_power" in em0:
                metrics["power"] = (
                    float(em0.get("a_act_power", 0.0))
                    + float(em0.get("b_act_power", 0.0))
                    + float(em0.get("c_act_power", 0.0))
                )
            if "a_voltage" in em0:
                metrics["voltage"] = float(em0["a_voltage"])
            if "a_current" in em0:
                metrics["current"] = (
                    float(em0.get("a_current", 0.0))
                    + float(em0.get("b_current", 0.0))
                    + float(em0.get("c_current", 0.0))
                )

        if "emdata:0" in params:
            emdata = params.get("emdata:0", {})
            if "total_act_energy" in emdata:
                metrics["energy"] = float(emdata["total_act_energy"]) / 1000.0  # Wh zu kWh

        # B) Shelly Plus 1PM, PlugS, Mini (switch:0, pm1:0)
        for switch_key in ["switch:0", "switch:1", "pm1:0", "input:0"]:
            if switch_key in params and isinstance(params[switch_key], dict):
                sw = params[switch_key]
                if "apower" in sw and sw["apower"] is not None:
                    metrics["power"] = float(sw["apower"])
                if "voltage" in sw and sw["voltage"] is not None:
                    metrics["voltage"] = float(sw["voltage"])
                if "current" in sw and sw["current"] is not None:
                    metrics["current"] = float(sw["current"])
                if "aenergy" in sw and isinstance(sw["aenergy"], dict):
                    if "total" in sw["aenergy"]:
                        metrics["energy"] = float(sw["aenergy"]["total"]) / 1000.0

        # C) Generische Metriken
        for generic_key in ["power", "apower", "power_w", "val", "value", "voltage", "current", "energy", "energy_kwh"]:
            if generic_key in params and params[generic_key] is not None:
                val = params[generic_key]
                if isinstance(val, (int, float)):
                    if generic_key in ["power", "apower", "power_w", "val", "value"]:
                        metrics["power"] = float(val)
                    elif generic_key in ["energy", "energy_kwh"]:
                        metrics["energy"] = float(val)
                    else:
                        metrics[generic_key] = float(val)

        # 5. Zeitstempel
        ts = None
        if "ts" in params:
            try:
                ts = timezone.datetime.fromtimestamp(float(params["ts"]), tz=timezone.utc)
            except Exception:
                ts = timezone.now()
        else:
            ts = timezone.now()

        # 6. An zentrale Ingest Pipeline übergeben
        if metrics:
            result = ingest_metric_payload(
                device=device,
                metrics=metrics,
                timestamp=ts,
                source="websocket",
                meta=meta,
            )
            logger.info(
                "[WS-Ingest] ✅ %s -> %s (Power: %s W, Home: %s)",
                identifier,
                metrics,
                metrics.get("power", "-"),
                home.name,
            )
            return {
                "status": "ok",
                "device": identifier,
                "metrics": metrics,
                "msg_id": data.get("id"),
            }

        return None
    except Exception as e:
        logger.exception("[WS-Ingest] Fehler beim Verarbeiten des WebSocket-Frames: %s", e)
        return None
    finally:
        close_old_connections()


class EnergyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = "energy"
        self.user_group_name = None
        self.token = None

        # 1. Token aus URL-Pfad oder Query-String extrahieren
        url_token = self.scope.get("url_route", {}).get("kwargs", {}).get("token")
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)

        self.token = url_token or query_params.get("token", [None])[0] or query_params.get("home_token", [None])[0]

        # 2. General group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # 3. User group wenn authentifiziert
        user = self.scope.get("user")
        if user and user.is_authenticated:
            self.user_group_name = f"energy_{user.id}"
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )

        await self.accept()
        logger.info(
            "[WebSocket:EnergyConsumer] Client verbunden (User: %s, Token: %s, Channel: %s)",
            user if user and user.is_authenticated else "Anonymous/Device",
            self.token,
            self.channel_name,
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        if self.user_group_name:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        logger.debug("[WebSocket:EnergyConsumer] Client getrennt: %s (Code: %s)", self.channel_name, close_code)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Wird aufgerufen, wenn ein Gerät (z. B. Shelly Outbound WebSocket)
        Telemetriedaten per WebSocket an Sharegy sendet.
        """
        payload = text_data
        if not payload and bytes_data:
            payload = bytes_data.decode("utf-8", errors="ignore")

        if not payload:
            return

        user = self.scope.get("user")
        res = await process_incoming_telemetry(self.token, payload, user)

        # Falls Shelly oder RPC-Client eine Request-ID geschickt hat, quittieren wir den Empfang:
        if res and res.get("msg_id") is not None:
            ack_msg = {
                "id": res["msg_id"],
                "src": "sharegy",
                "result": {"status": "ok", "device": res["device"]},
            }
            await self.send(text_data=json.dumps(ack_msg))

    async def send_energy_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def send_device_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))