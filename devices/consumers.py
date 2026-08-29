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

logger = logging.getLogger(__name__)


@database_sync_to_async
def process_incoming_telemetry(token, payload_str, user):
    """
    100% DAU-sichere Ingestion von WebSocket-Frames
    (Shelly Outbound WebSocket RPC NotifyStatus / Shelly.GetStatus, Tasmota, ioBroker, Custom Frames).
    """
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

        # 2. Device Identifier ermitteln
        raw_src = (
            data.get("src")
            or data.get("device_id")
            or data.get("identifier")
            or data.get("id")
            or data.get("mac")
            or "shelly_device"
        )
        identifier = str(raw_src).strip()

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


        # 4. Metriken extrahieren (Unterstützt params, result oder flaches JSON)
        metrics = {}
        meta = {"from": "websocket", "src": identifier}

        container = data.get("params") or data.get("result") or data

        if not isinstance(container, dict):
            return None

        total_power = 0.0
        has_power = False
        total_energy = 0.0
        has_energy = False

        # Alle Unterstrukturen durchsuchen (em:0, em:1, switch:0, pm1:0, etc.)
        for key, val in container.items():
            if isinstance(val, dict):
                # A) 3-Phasen Messung (Shelly 3EM / Pro 3EM)
                if "total_act_power" in val and val["total_act_power"] is not None:
                    total_power += float(val["total_act_power"])
                    has_power = True
                elif "a_act_power" in val:
                    p = (
                        float(val.get("a_act_power") or 0.0)
                        + float(val.get("b_act_power") or 0.0)
                        + float(val.get("c_act_power") or 0.0)
                    )
                    total_power += p
                    has_power = True

                # B) Einzelrelais / Smart Plugs (Shelly Plus 1PM, Shelly 1PM Gen3, PlugS)
                if "apower" in val and val["apower"] is not None:
                    total_power += float(val["apower"])
                    has_power = True
                if "power" in val and val["power"] is not None:
                    total_power += float(val["power"])
                    has_power = True

                # Spannung & Strom
                if "voltage" in val and val["voltage"] is not None:
                    metrics["voltage"] = float(val["voltage"])
                elif "a_voltage" in val and val["a_voltage"] is not None:
                    metrics["voltage"] = float(val["a_voltage"])

                if "current" in val and val["current"] is not None:
                    metrics["current"] = float(val["current"])
                elif "a_current" in val and val["a_current"] is not None:
                    metrics["current"] = (
                        float(val.get("a_current") or 0.0)
                        + float(val.get("b_current") or 0.0)
                        + float(val.get("c_current") or 0.0)
                    )

                # Energie
                if "total_act_energy" in val and val["total_act_energy"] is not None:
                    total_energy += float(val["total_act_energy"]) / 1000.0
                    has_energy = True
                elif "aenergy" in val and isinstance(val["aenergy"], dict):
                    if "total" in val["aenergy"] and val["aenergy"]["total"] is not None:
                        total_energy += float(val["aenergy"]["total"]) / 1000.0
                        has_energy = True

            elif isinstance(val, (int, float)):
                if key in ["power", "apower", "power_w", "val", "value"]:
                    total_power += float(val)
                    has_power = True
                elif key in ["energy", "energy_kwh", "total_energy"]:
                    total_energy += float(val)
                    has_energy = True
                elif key in ["voltage", "current"]:
                    metrics[key] = float(val)

        if has_power:
            metrics["power"] = round(total_power, 2)
        if has_energy:
            metrics["energy"] = round(total_energy, 4)

        # 5. Zeitstempel
        ts = timezone.now()
        raw_ts = container.get("ts") or data.get("ts")
        if raw_ts:
            try:
                ts = timezone.datetime.fromtimestamp(float(raw_ts), tz=timezone.utc)
            except Exception:
                ts = timezone.now()

        # 6. Ingest & Live-Broadcast an Dashboards
        if metrics:
            ingest_metric_payload(
                device=device,
                metrics=metrics,
                timestamp=ts,
                source="shelly_ws",
                meta=meta,
            )
            logger.info(
                "[WS-Ingest] ✅ %s -> %s W (Home: %s)",
                identifier,
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

        logger.debug("[WebSocket:EnergyConsumer] 🔌 Client getrennt: %s (Code: %s)", self.channel_name, close_code)

    async def receive(self, text_data=None, bytes_data=None):
        payload = text_data
        if not payload and bytes_data:
            payload = bytes_data.decode("utf-8", errors="ignore")

        if not payload:
            return

        user = self.scope.get("user")
        res = await process_incoming_telemetry(self.token, payload, user)

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

    async def send_energy_update(self, event):
        # Nur an Browser-Clients senden, nicht an den Shelly selbst!
        if not self.is_device:
            await self.send(text_data=json.dumps(event["data"]))

    async def send_device_update(self, event):
        # Nur an Browser-Clients senden, nicht an den Shelly selbst!
        if not self.is_device:
            await self.send(text_data=json.dumps(event["data"]))