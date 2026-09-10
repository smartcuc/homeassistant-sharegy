######################
# devices/consumers.py
######################

import json
import logging
import asyncio
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.db import close_old_connections
from django.core.cache import cache


logger = logging.getLogger(__name__)


@database_sync_to_async
def process_incoming_telemetry(token, payload_str, user):
    """
    100% DAU-sichere Ingestion von WebSocket-Frames
    (Shelly Outbound WebSocket RPC NotifyStatus / Shelly.GetStatus, Tasmota, ioBroker, Custom Frames).
    """
    from django.db import connection, InterfaceError, OperationalError
    from devices.models import Home, Device
    from devices.services.ingest import ingest_metric_payload

    close_old_connections()
    try:
        try:
            data = json.loads(payload_str)
        except Exception:
            logger.warning("[WS-Ingest] Ungültiges JSON empfangen: %s", str(payload_str)[:100])
            return None


        if not isinstance(data, dict):
            return None

        # 1. Home ermitteln (maximal fehlertolerant)
        home = None
        if token:
            clean_tok = str(token).strip()
            no_hyphens = clean_tok.replace("-", "")

            # A) User UUID / User ID matching (Priorität 1)
            try:
                home = Home.objects.filter(user__id=clean_tok).select_related("user").first()
            except Exception:
                pass

            # B) Direkte Suche nach mqtt_token (exakt oder auf 16 Zeichen gekürzt)
            if not home:
                home = (
                    Home.objects.filter(mqtt_token__iexact=clean_tok).select_related("user").first()
                    or Home.objects.filter(mqtt_token__iexact=clean_tok[:16]).select_related("user").first()
                    or Home.objects.filter(mqtt_token__iexact=no_hyphens).select_related("user").first()
                    or Home.objects.filter(mqtt_token__iexact=no_hyphens[:16]).select_related("user").first()
                    or Home.objects.filter(mqtt_token__istartswith=clean_tok[:8]).select_related("user").first()
                )

            # C) Suche nach Email
            if not home:
                home = Home.objects.filter(user__email__iexact=clean_tok).select_related("user").first()

            # D) Suche nach numerischer Home ID
            if not home and clean_tok.isdigit():
                try:
                    home = Home.objects.filter(id=int(clean_tok)).select_related("user").first()
                except Exception:
                    pass

        # E) Authentifizierter User Fallback
        if not home and user and user.is_authenticated:
            home = Home.objects.filter(user=user).select_related("user").first()

        # F) Token aus JSON-Body
        if not home:
            body_token = str(data.get("token") or data.get("home_token") or data.get("user_id") or "").strip()
            if body_token:
                no_hy = body_token.replace("-", "")
                try:
                    home = Home.objects.filter(user__id=body_token).select_related("user").first()
                except Exception:
                    pass
                if not home:
                    home = (
                        Home.objects.filter(mqtt_token__iexact=body_token).select_related("user").first()
                        or Home.objects.filter(mqtt_token__iexact=body_token[:16]).select_related("user").first()
                        or Home.objects.filter(mqtt_token__iexact=no_hy[:16]).select_related("user").first()
                    )

        # G) Systemweiter Single-Home Fallback
        if not home:
            home = Home.objects.first()

        if not home:
            logger.warning("[WS-Ingest] Kein Haushalt in der Datenbank gefunden.")
            return None

        # 2. Sensor-Adapter Ingestion Pipeline (Shelly, Waveshare, Tasmota, Generic)
        from devices.adapters.sensors import SensorAdapterRegistry, process_canonical_sensor_reading

        reading = SensorAdapterRegistry.detect_and_parse(data)
        identifier = str(reading.device_identifier or data.get("src") or data.get("device_id") or data.get("id") or "sensor_device").strip()

        # 3. Device finden oder anlegen (und falls zuvor im falschen Test-Home angelegt, automatisch umhängen!)
        device = Device.objects.filter(identifier=identifier).first()
        if device:
            if device.home_id != home.id:
                device.home = home
                device.save(update_fields=["home"])
                logger.info("[WS-Ingest] 🔄 Gerät %s wurde zu Haushalt '%s' verschoben.", identifier, home.name)
        else:
            device = Device.objects.create(
                home=home,
                identifier=identifier,
                configured=True,
                active=True,
            )
            logger.info("[WS-Ingest] 🚀 Neues Gerät per WebSocket automatisch entdeckt: %s (Haushalt: %s)", identifier, home.name)

        # 4. Standard-Ingest über Canonical Sensor Pipeline
        metrics = process_canonical_sensor_reading(device=device, reading=reading, source="websocket")
        relay_state = reading.relay_state

        # 4b. Track active interface source
        try:
            from devices.services.interface_tracker import track_interface_telemetry
            src_tag = (
                data.get("source")
                or data.get("client")
                or ("shelly" if ("shelly" in identifier.lower() or data.get("method") in ("NotifyStatus", "Shelly.GetStatus")) else "websocket")
            )
            track_interface_telemetry(home.id, src_tag, data)
        except Exception:
            pass

        if relay_state is not None:
            cache.set(f"device_relay_state_{device.id}", relay_state, timeout=86400)
            cache.set(f"device_switchable_{device.id}", True, timeout=86400)

            # Live-Broadcast an geöffnete Web-Dashboards
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        "energy",
                        {
                            "type": "send_device_update",
                            "data": {
                                "type": "device_relay_update",
                                "device_id": device.id,
                                "identifier": identifier,
                                "relay_state": relay_state,
                            }
                        }
                    )
            except Exception:
                pass

        # 5. Ingest & Live-Broadcast an Dashboards
        if metrics or relay_state is not None:
            meta = {"from": "websocket", "src": identifier}
            unit_map = {"power": "W", "energy": "kWh", "voltage": "V", "current": "A", "battery_soc": "%"}
            ingest_metric_payload(
                device=device,
                metrics=metrics,
                unit_map=unit_map,
                timestamp=reading.timestamp,
                source="websocket",
                meta=meta,
            )
            logger.info(
                "[WS-Ingest] ✅ %s -> %s W (Relais: %s, Home: %s)",
                identifier,
                metrics.get("power", "-"),
                "AN" if relay_state is True else ("AUS" if relay_state is False else "-"),
                home.name,
            )
            return {
                "status": "ok",
                "device": identifier,
                "device_id": device.id,
                "home_id": home.id,
                "relay_state": relay_state,
                "metrics": metrics,
                "msg_id": data.get("id"),
            }

        return None
    except (InterfaceError, OperationalError) as db_err:
        try:
            connection.close()
        except Exception:
            pass
        logger.warning("[WS-Ingest] DB-Verbindung getrennt, Verbindung wird für nächsten Frame zurückgesetzt: %s", db_err)
        return None
    except Exception as e:
        logger.exception("[WS-Ingest] Fehler beim Verarbeiten des Frames: %s", e)
        return None
    finally:
        close_old_connections()



class EnergyConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.poll_task = None
        self.msg_counter = 1
        self.is_device = False
        self.joined_devices = set()


    async def connect(self):
        self.group_name = "energy"
        self.user_group_name = None
        self.token = None

        # 1. Token aus URL-Pfad oder Query-String extrahieren
        url_token = self.scope.get("url_route", {}).get("kwargs", {}).get("token")
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)

        self.token = (
            url_token
            or query_params.get("token", [None])[0]
            or query_params.get("home_token", [None])[0]
            or query_params.get("user", [None])[0]
        )

        user = self.scope.get("user")

        # 2. Unterscheidung zwischen Frontend-Browser und Shelly-Gerät:
        # Wenn ein Token in der URL übergeben wird, ist es ein Ingestion-Client (Shelly)
        if self.token:
            self.is_device = True
        else:
            self.is_device = False

        # 3. Nur Browser-Clients treten der Broadcast-Gruppe bei
        if not self.is_device:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            if user and user.is_authenticated:
                self.user_group_name = f"energy_{user.id}"
                await self.channel_layer.group_add(self.user_group_name, self.channel_name)

        await self.accept()
        logger.info(
            "[WebSocket:EnergyConsumer] 🔌 %s verbunden (User: %s, Token: %s, Channel: %s)",
            "Gerät (Shelly)" if self.is_device else "Browser-Client",
            user if user and user.is_authenticated else "Anonymous/Device",
            self.token,
            self.channel_name,
        )

        # 4. Wenn ein Shelly verbunden ist: Initialen Status anfordern & zyklisch abfragen
        if self.is_device:
            try:
                get_status_req = {
                    "id": self.msg_counter,
                    "src": "sharegy",
                    "method": "Shelly.GetStatus",
                }
                self.msg_counter += 1
                await self.send(text_data=json.dumps(get_status_req))
            except Exception:
                pass

            self.poll_task = asyncio.create_task(self._periodic_shelly_poller())

    async def _periodic_shelly_poller(self):
        """Fragt den Shelly alle 5 Sekunden nach dem aktuellen Status."""
        try:
            while True:
                await asyncio.sleep(5)
                req = {
                    "id": self.msg_counter,
                    "src": "sharegy",
                    "method": "Shelly.GetStatus",
                }
                self.msg_counter += 1
                await self.send(text_data=json.dumps(req))
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    async def disconnect(self, close_code):
        if self.poll_task:
            self.poll_task.cancel()

        if not self.is_device:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            if self.user_group_name:
                await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        else:
            for grp in self.joined_devices:
                try:
                    await self.channel_layer.group_discard(grp, self.channel_name)
                except Exception:
                    pass

        logger.debug("[WebSocket:EnergyConsumer] 🔌 Client getrennt: %s (Code: %s)", self.channel_name, close_code)

    async def receive(self, text_data=None, bytes_data=None):
        payload = text_data
        if not payload and bytes_data:
            payload = bytes_data.decode("utf-8", errors="ignore")

        if not payload:
            return

        # Schnelle Beantwortung von Ping / Keep-Alive Frames
        clean_p = payload.strip()
        if clean_p in ('{"method":"ping"}', '{"method": "ping"}', '{"type":"ping"}', '{"type": "ping"}', 'ping'):
            try:
                await self.send(text_data=json.dumps({"type": "pong", "status": "ok"}))
            except Exception:
                pass
            return

        user = self.scope.get("user")
        res = await process_incoming_telemetry(self.token, payload, user)

        # Wenn ein Gerät identifiziert wurde, dynamisch der Channel-Gruppe für Aktorik beitreten
        if res and self.is_device:
            if res.get("home_id"):
                home_grp = f"home_{res['home_id']}"
                if home_grp not in self.joined_devices:
                    await self.channel_layer.group_add(home_grp, self.channel_name)
                    self.joined_devices.add(home_grp)

            if res.get("device_id"):
                dev_id = res["device_id"]
                dev_ident = res.get("device")
                grp_id = f"device_{dev_id}"
                grp_ident = f"device_{dev_ident}"
                if grp_id not in self.joined_devices:
                    await self.channel_layer.group_add(grp_id, self.channel_name)
                    self.joined_devices.add(grp_id)
                if grp_ident and grp_ident not in self.joined_devices:
                    await self.channel_layer.group_add(grp_ident, self.channel_name)
                    self.joined_devices.add(grp_ident)

        # Quittierung nur an den Shelly zurücksenden falls er eine ID mitgeschickt hat
        if res and res.get("msg_id") is not None and self.is_device:
            try:
                ack_msg = {
                    "id": res["msg_id"],
                    "src": "sharegy",
                    "result": {"status": "ok", "device": res["device"]},
                }
                await self.send(text_data=json.dumps(ack_msg))
            except Exception:
                pass

    async def relay_command(self, event):
        """
        Empfängt einen Schaltbefehl aus dem Channel-Layer (z. B. ausgelöst per REST API)
        und sendet einen standardisierten Shelly Gen2/Gen3 RPC Frame über die WebSocket-Verbindung.
        """
        if self.is_device:
            cmd = event.get("command", "toggle")  # "on", "off", "toggle"
            channel = event.get("channel", 0)
            rpc_req = {
                "id": self.msg_counter,
                "src": "sharegy",
                "method": "Switch.Set" if cmd in ("on", "off") else "Switch.Toggle",
                "params": {
                    "id": channel,
                },
            }
            if cmd in ("on", "off"):
                rpc_req["params"]["on"] = (cmd == "on")

            self.msg_counter += 1
            logger.info("[WebSocket:EnergyConsumer] ⚡ Sende Schaltbefehl an Relais: %s", rpc_req)
            await self.send(text_data=json.dumps(rpc_req))

    async def device_control_event(self, event):
        """
        Empfängt gerätebezogene Steuerungsbefehle (z. B. FBH-Aktorik, BWWP SG-Ready)
        und leitet sie an verbundene Clients / ioBroker weiter.
        """
        try:
            payload = {
                "id": self.msg_counter,
                "src": "sharegy",
                "method": event.get("action", "Switch.Set"),
                "params": event.get("params", {}),
                "device_id": event.get("device_id"),
                "identifier": event.get("identifier"),
                "val": event.get("val"),
                "value": event.get("value"),
                "action": event.get("action"),
                "flow_temp_setpoint_c": event.get("flow_temp_setpoint_c"),
                "predictive_mpc": event.get("predictive_mpc"),
            }
            self.msg_counter += 1
            await self.send(text_data=json.dumps(payload))
        except Exception as e:
            logger.debug("[EnergyConsumer] Fehler beim Senden von device_control_event: %s", e)

    async def schedule_sync_event(self, event):
        """
        Empfängt 24h MPC-Fahrpläne und synct diese an verbundene Bridges / ioBroker für Offline-Resilienz.
        """
        try:
            payload = {
                "type": "schedule_sync",
                "timeline": event.get("timeline", []),
                "best_preheat_window": event.get("best_preheat_window"),
                "flow_temp_setpoint_c": event.get("flow_temp_setpoint_c"),
                "mode": event.get("mode"),
                "ts": int(timezone.now().timestamp()),
            }
            await self.send(text_data=json.dumps(payload))
        except Exception as e:
            logger.debug("[EnergyConsumer] Fehler beim Senden von schedule_sync_event: %s", e)

    async def send_energy_update(self, event):
        # Nur an Browser-Clients senden, nicht an den Shelly selbst!
        if not self.is_device:
            await self.send(text_data=json.dumps(event["data"]))

    async def send_device_update(self, event):
        # Nur an Browser-Clients senden, nicht an den Shelly selbst!
        if not self.is_device:
            await self.send(text_data=json.dumps(event["data"]))