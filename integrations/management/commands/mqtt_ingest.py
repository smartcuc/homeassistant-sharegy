#################################################
# integrations\management\commands\mqtt_ingest.py
#################################################

import json
import os
import re
import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import close_old_connections, InterfaceError, OperationalError

import paho.mqtt.client as mqtt  # pip install paho-mqtt

from integrations.models import InboundWebhookEvent
from integrations.tasks import process_inbound_webhook_event
from core.models import Meter


logger = logging.getLogger(__name__)


def _parse_iso(ts: str):
    # akzeptiert "Z" und ISO8601
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _extract_serial_from_topic(topic: str) -> str | None:
    """
    Unterstützt typische Topic-Designs:
      - meter/<serial>/readings
      - device/<serial>/realtime
    """
    m = re.match(r"^(meter|device)/([^/]+)/", topic)
    if m:
        return m.group(2)
    return None


def _normalize_payload(topic: str, raw: bytes) -> tuple[str | None, dict | None]:
    """
    Erwartet JSON Payload.
    Unterstützte Formen:
      A) {"meter_serial":"ABC","ts_start":"...","obis":"1.8.0","value":12.3,"unit":"kWh"}
      B) {"meter_serial":"ABC","readings":[{...},{...}]}
      C) {"readings":[{ "meter_serial":"ABC", ... }]}  # meter_serial je reading
    Gibt (meter_serial, payload_for_event) zurück.
    """
    try:
        msg = json.loads(raw.decode("utf-8"))
    except Exception:
        logger.exception("mqtt.payload.invalid_json")
        return None, None

    serial = (
        msg.get("meter_serial")
        or msg.get("serial_number")
        or _extract_serial_from_topic(topic)
    )

    # Falls payload direkt readings enthält:
    if (
        isinstance(msg, dict)
        and "readings" in msg
        and isinstance(msg["readings"], list)
    ):
        readings = msg["readings"]
        # meter_serial ggf. pro reading oder global:
        if serial:
            for r in readings:
                r.setdefault("meter_serial", serial)
        else:
            # versuche aus erstem reading
            if readings and isinstance(readings[0], dict):
                serial = readings[0].get("meter_serial")
        return serial, {"readings": readings}

    # Single reading:
    if serial and "ts_start" in msg:
        reading = {
            "meter_serial": serial,
            "ts_start": msg["ts_start"],
            "obis": msg.get("obis", "1.8.0"),
            # akzeptiere value oder value_kwh
            "value_kwh": msg.get("value_kwh", msg.get("value")),
            "unit": msg.get("unit", "kWh"),
        }
        return serial, {"readings": [reading]}

    logger.warning("mqtt.payload.unrecognized_format", extra={"topic": topic})
    return None, None


class Command(BaseCommand):
    help = "MQTT ingestion listener: subscribes to topics and writes InboundWebhookEvent + triggers Celery processing."

    def add_arguments(self, parser):
        parser.add_argument("--broker", default=os.getenv("MQTT_HOST", "127.0.0.1"))
        parser.add_argument(
            "--port", type=int, default=int(os.getenv("MQTT_PORT", "1883"))
        )
        parser.add_argument("--username", default=os.getenv("MQTT_USERNAME", ""))
        parser.add_argument("--password", default=os.getenv("MQTT_PASSWORD", ""))
        parser.add_argument(
            "--topic",
            default=os.getenv("MQTT_TOPIC", "meter/+/readings"),
            help="MQTT subscribe topic, supports wildcards",
        )
        parser.add_argument("--qos", type=int, default=int(os.getenv("MQTT_QOS", "1")))
        parser.add_argument(
            "--client-id", default=os.getenv("MQTT_CLIENT_ID", "eswes-ingest")
        )
        parser.add_argument(
            "--default-tenant-id",
            default=os.getenv("MQTT_DEFAULT_TENANT_ID", ""),
            help="Optional: UUID of a tenant to attach unknown meters to (otherwise message is dropped).",
        )

    def handle(self, *args, **opts):
        broker = opts["broker"]
        port = opts["port"]
        username = opts["username"]
        password = opts["password"]
        topic = opts["topic"]
        qos = opts["qos"]
        client_id = opts["client_id"]
        default_tenant_id = opts["default_tenant_id"]

        self.stdout.write(
            self.style.SUCCESS(
                f"MQTT ingest starting. broker={broker}:{port} topic={topic} qos={qos}"
            )
        )

        client = mqtt.Client(
            client_id=client_id, reconnect_on_failure=True
        )  # reconnect supported 【2-9e834f】
        if username:
            client.username_pw_set(username, password)

        def on_connect(c, userdata, flags, rc, properties=None):
            # subscribe im on_connect → bei reconnect wieder da 【7-49649e】
            if rc == 0:
                logger.info(
                    "mqtt.connected",
                    extra={"broker": broker, "topic": topic, "qos": qos},
                )
                c.subscribe(topic, qos=qos)  # subscribe API 【6-7a7b01】
            else:
                logger.error("mqtt.connect.failed", extra={"rc": rc})

        def on_message(c, userdata, msg):
            close_old_connections()
            try:
                serial, payload = _normalize_payload(msg.topic, msg.payload)
                if not serial or not payload:
                    return

                meter = (
                    Meter.objects.filter(serial_number=serial)
                    .select_related("tenant")
                    .first()
                )

                # Tenant Mapping: über serial_number → Meter → tenant
                tenant = meter.tenant if meter else None

                if not tenant and default_tenant_id:
                    # optionaler Fallback
                    tenant = (
                        type(meter)
                        .tenant.field.related_model.objects.filter(id=default_tenant_id)
                        .first()
                    )

                if not tenant:
                    logger.warning(
                        "mqtt.unknown_meter_or_tenant",
                        extra={"serial": serial, "topic": msg.topic},
                    )
                    return

                # Audit Event speichern
                evt = InboundWebhookEvent.objects.create(
                    tenant=tenant,
                    event_type="MQTT",
                    status=InboundWebhookEvent.Status.RECEIVED,
                    payload=payload,
                )

                # Celery Processing triggern
                process_inbound_webhook_event.delay(str(evt.id))

                logger.info(
                    "mqtt.event.accepted", extra={"event_id": str(evt.id), "serial": serial}
                )
            except (InterfaceError, OperationalError) as db_err:
                logger.warning("DB connection lost in mqtt_ingest (%s), reset connection...", db_err)
                close_old_connections()
            except Exception as e:
                logger.exception("Error in mqtt_ingest on_message: %s", e)
            finally:
                close_old_connections()


        client.on_connect = on_connect
        client.on_message = on_message

        # connect + loop_forever: blockierend, stabil für daemon 【8-323795】【2-9e834f】
        client.connect(broker, port, keepalive=60)
        client.loop_forever()
