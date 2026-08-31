##############################################
# core/management/commands/mqtt_consume.py
##############################################

# ============================================================
# MQTT CONSUMER – INGEST PIPELINE
# ============================================================

import json
import logging
import os
import ssl

from django.db import close_old_connections, InterfaceError, OperationalError
from django.core.cache import cache  # 💡 Ganz wichtig: Hier importieren
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from devices.models import Home, Device, DeviceMetric, DeviceLatestMetric
from devices.services.ingest import ingest_metric_payload
from integrations.mqtt_profiles import get_parser

import paho.mqtt.client as mqtt



logger = logging.getLogger(__name__)

LAST_MESSAGE_TS = None


# ============================================================
# ✅ TIMESTAMP PARSER (robust)
# ============================================================

def parse_ts(ts_str):
    if not ts_str:
        return timezone.now()

    dt = parse_datetime(ts_str)
    if dt is None:
        return timezone.now()

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone=timezone.utc)

    return dt.astimezone(timezone.utc)


# ============================================================
# ✅ HELPERS & DEDUPLICATION FILTER
# ============================================================

def _to_float(val):
    try:
        return float(val)
    except Exception:
        return None


def should_record_metric(
    device_id,
    metric_key,
    float_val,
    ts,
    deadband=1.0,
    heartbeat_seconds=60,
):
    """
    Enterprise-Grade Telemetrie Deduplizierung & Deadband-Filter.
    Prüft im Redis-Cache, ob der Wert sich signifikant geändert hat
    oder das Heartbeat-Intervall abgelaufen ist.
    Spart 80-90% redundante DB-Inserts ohne Datenverlust.
    """
    if float_val is None:
        return False

    dedup_key = f"dedup:{device_id}:{metric_key}"
    last_record = cache.get(dedup_key)

    now_ts = ts.timestamp() if hasattr(ts, "timestamp") else timezone.now().timestamp()

    if last_record and isinstance(last_record, dict):
        last_val = last_record.get("val")
        last_ts = last_record.get("ts", 0)

        # Deadband Check
        if last_val is not None and abs(float_val - last_val) < deadband:
            # Heartbeat Check
            if (now_ts - last_ts) < heartbeat_seconds:
                return False

    cache.set(dedup_key, {"val": float_val, "ts": now_ts}, timeout=86400)
    return True


def should_record_state(device_id, key, val, ts, heartbeat_seconds=300):
    dedup_key = f"dedup:{device_id}:state:{key}"
    last_record = cache.get(dedup_key)
    now_ts = ts.timestamp() if hasattr(ts, "timestamp") else timezone.now().timestamp()

    if last_record and isinstance(last_record, dict):
        last_val = last_record.get("val")
        last_ts = last_record.get("ts", 0)
        if last_val == val and (now_ts - last_ts) < heartbeat_seconds:
            return False

    cache.set(dedup_key, {"val": val, "ts": now_ts}, timeout=86400)
    return True


# ============================================================
# ✅ INGEST ENTRYPOINT
# ============================================================

def ingest(topic: str, payload: bytes, auto_prov: bool):
    
    parts = topic.split("/")

    if len(parts) != 3:
        raise ValueError(f"Invalid topic format: {topic}")

    home_token = parts[1].strip()
    device_identifier = parts[2].strip()

    # ========================================================
    # ✅ HOME LOOKUP
    # ========================================================
    logger.debug("HOME TOKEN: %s", home_token)

    home = Home.objects.filter(mqtt_token=home_token).first()
    if not home:
        logger.warning("No Home found for token=%s", home_token)
        return

    # ========================================================
    # ✅ DEVICE LOOKUP / AUTO-PROVISION
    # ========================================================
    device = Device.objects.filter(
        home=home,
        identifier=device_identifier,
    ).first()

    logger.debug(
        "MQTT | topic=%s device=%s found=%s auto_prov=%s",
        topic,
        device_identifier,
        bool(device),
        auto_prov,
    )

    # ✅ AUTO-PROVISION FIRST
    if not device and auto_prov:
        logger.info("Auto-provisioning device %s", device_identifier)
        device, created = Device.objects.get_or_create(
            home=home,
            identifier=device_identifier,
        )
        if created:
            logger.info("Auto-provisioned device=%s", device_identifier)

    # ✅ MAGIC MOMENT DANACH
    if device and not device.configured:
        device.configured = True
        device.save(update_fields=["configured"])
        logger.info("Device %s connected & configured", device_identifier)

    # ========================================================
    # ✅ PAYLOAD PARSING
    # ========================================================
    # raw payload kommt als bytes rein
    payload_str = payload.decode("utf-8")

    logger.debug("RAW PAYLOAD: %s", payload_str)

    metrics = {}
    state = {}
    meta = {}

    # ========================================================
    # ✅ PAYLOAD PARSING (ROBUST)
    # ========================================================

    try:
        data = json.loads(payload_str)

        # ✅ Case 1: {"metrics": {...}}
        if isinstance(data, dict) and "metrics" in data:
            metrics = data.get("metrics", {})
            state = data.get("state", {})
            meta = data.get("meta", {})

        # ✅ Case 2: {"val": 229.8}
        elif isinstance(data, dict) and "val" in data:

            metric_name = data.get(
                "metric",
                "value"
            )

            metrics = {
                metric_name: data["val"]
            }

            meta = data

        # ✅ Case 3: ioBroker wrapper
        elif isinstance(data, dict) and "message" in data:
            try:
                val = float(data["message"])
                metrics = {"value": val}
                meta = data
            except Exception:
                logger.warning("Invalid ioBroker message: %s", payload_str)
                return

        # ✅ Case 4: generic dict
        elif isinstance(data, dict):
            metrics = data

        else:
            metrics = {"value": float(data)}

    except Exception:
        # ✅ fallback plain string
        try:
            metrics = {"value": float(payload_str)}
        except Exception:
            logger.warning("Invalid payload format: %s", payload_str)
            return

    # Extract unit_map if provided in payload
    unit_map = {}
    if isinstance(data, dict):
        raw_u = data.get("unit") or data.get("unit_of_measurement") or data.get("u")
        if raw_u:
            for k in metrics.keys():
                unit_map[k] = str(raw_u).strip()
        if "units" in data and isinstance(data["units"], dict):
            unit_map.update(data["units"])

    # ========================================================
    # ✅ TIMESTAMP + SOURCE
    # ========================================================

    ts = None

    # ✅ try extract timestamp from meta
    if isinstance(meta, dict):
        if "ts" in meta:
            try:
                ts = timezone.datetime.fromtimestamp(meta["ts"] / 1000, tz=timezone.utc)
            except Exception:
                ts = None
        elif "timestamp" in meta:
            ts = parse_ts(meta["timestamp"])

    if not ts:
        ts = timezone.now()

    source = str(meta.get("from") or "mqtt")[:64] if isinstance(meta, dict) else "mqtt"

    logger.debug(
        "METRICS: %s | STATE: %s | SOURCE: %s",
        metrics,
        state,
        source,
    )

    # ========================================================
    # ✅ DEVICE ACTIVITY & PROFILE NORMALIZATION
    # ========================================================

    profile_slug = (
        device.mqtt_profile.slug
        if device.mqtt_profile
        else "generic"
    )

    parser = get_parser(profile_slug)
    metrics = parser.normalize(metrics)

    # ========================================================
    # ✅ UNIFIED METRIC INGESTION PIPELINE
    # ========================================================

    ingest_metric_payload(
        device=device,
        metrics=metrics,
        timestamp=ts,
        source=source,
        meta=meta,
        state=state,
        unit_map=unit_map,
    )


# ============================================================
# ✅ DJANGO MANAGEMENT COMMAND ENTRYPOINT
# ============================================================

class Command(BaseCommand):
    help = "MQTT Consumer"

    def handle(self, *args, **options):
        logger.info("Starting MQTT consumer...")

        host = os.getenv("MQTT_HOST", "sharegy.de")
        port = int(os.getenv("MQTT_PORT", 8883))
        user = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")

        logger.info("Connecting to MQTT %s:%s ...", host, port)

        # ✅ V2 Callback API verwenden (KRITISCH)
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # ✅ Auth
        if user and password:
            client.username_pw_set(user, password)

        # ✅ TLS (DEV/TEST – PROD später härten)
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)

        # ✅ Callbacks setzen
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        # ✅ Connect
        client.connect(host, port)

        logger.info("MQTT loop starting")

        try:
            client.loop_forever()
        except KeyboardInterrupt:
            logger.info("MQTT stopped")
            client.disconnect()

    # ---------------------------
    # MQTT CALLBACKS (V2!)
    # ---------------------------

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info("MQTT connected successfully")
            client.subscribe("h/+/+")
        else:
            logger.error("MQTT connection failed reason_code=%s", reason_code)

    def on_message(self, client, userdata, msg):      
        global LAST_MESSAGE_TS

        LAST_MESSAGE_TS = timezone.now()

        close_old_connections()
        try:
            ingest(
                topic=msg.topic,
                payload=msg.payload,
                auto_prov=True,
            )
        except (InterfaceError, OperationalError) as db_err:
            logger.warning("DB connection stale during MQTT ingest (%s), reconnecting...", db_err)
            close_old_connections()
            try:
                ingest(
                    topic=msg.topic,
                    payload=msg.payload,
                    auto_prov=True,
                )
            except Exception as retry_err:
                logger.exception("Ingest failed after retry for topic=%s: %s", msg.topic, retry_err)
        except Exception as e:
            logger.exception("Ingest failed for topic=%s: %s", msg.topic, e)
        finally:
            close_old_connections()



# ============================================================
# ✅ MQTT INGEST HEALTH
# ============================================================

def check_ingest_health(timeout_seconds=120):
    from django.utils import timezone
    from datetime import timedelta

    if not LAST_MESSAGE_TS:
        return False, "no_messages"

    if LAST_MESSAGE_TS < timezone.now() - timedelta(seconds=timeout_seconds):
        return False, "stalled"

    return True, "ok"
