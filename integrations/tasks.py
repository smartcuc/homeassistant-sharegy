##########################
# integrations/tasks.py
##########################

import logging
import os
import json
import redis

from decimal import Decimal
from datetime import datetime

from celery import shared_task
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from integrations.models import InboundWebhookEvent
from integrations.services_tibber import (
    upsert_tibber_interval_readings,
)

from core.models import IntervalReading, MeterRegister
from devices.models import Device, DeviceMetric
from devices.services.ingest import ingest_metric_payload

from core.models import Meter
from core.constants.obis import OBIS_MAP
from core.services_validation import validate_obis_reading
from billing.tasks import recalculate_late_slot

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer






logger = logging.getLogger(__name__)


############################################################
# 🔵 1. WEBHOOK PROCESSING (unverändert – nur leicht cleaner)
############################################################


@shared_task(bind=True, max_retries=5)
def process_inbound_webhook_event(self, event_id: str):

    evt = InboundWebhookEvent.objects.select_related("tenant").get(id=event_id)

    if evt.processed_at:
        logger.info("event.already_processed")
        return {"status": "already_processed"}

    written = 0
    final_status = None
    final_error = ""

    try:
        payload = evt.payload or {}
        tenant = evt.tenant

        for r in payload.get("readings", []):

            # ✅ 1. METER
            serial = r["meter_serial"]

            meter, _ = Meter.objects.get_or_create(
                serial_number=serial,
                defaults={"tenant": tenant},
            )

            # ✅ 2. ZEIT
            ts = datetime.fromisoformat(r["ts_start"].replace("Z", "+00:00"))
            received_at = timezone.now()

            # ✅ 3. OBIS
            obis = r.get("obis", "1.8.0")
            obis_meta = OBIS_MAP.get(obis, {})
            unit = r.get("unit", obis_meta.get("unit", "kWh"))

            # ✅ 4. VALUE & VALIDIERUNG
            raw_val = Decimal(str(r["value_kwh"]))
            validation = validate_obis_reading(obis, raw_val, unit)
            if not validation["is_valid"]:
                logger.warning("Reading rejected by validation: %s", validation.get("error"))
                continue
            value = validation["sanitized_value"]

            # ✅ 5. LATE LOGIC
            delay = (received_at - ts).total_seconds()
            is_late = delay > 60

            # ✅ 6. DUPLICATES & UPDATES
            existing = IntervalReading.objects.filter(
                meter=meter,
                ts_start=ts,
                obis_code=obis,
            ).first()

            if existing:
                if existing.value == value:
                    continue
                else:
                    existing.value = value
                    existing.received_at = received_at
                    existing.is_late = is_late
                    existing.ingestion_delay_seconds = int(delay)
                    existing.save()
                    # Bei Wertänderung: Sofortige Nachberechnung triggern
                    try:
                        recalculate_late_slot.delay(str(meter.id), ts.isoformat())
                    except Exception:
                        pass
                    continue

            # ✅ 7. REGISTER
            MeterRegister.objects.get_or_create(meter=meter, obis_code=obis)

            # ✅ 8. SAVE
            IntervalReading.objects.create(
                tenant=tenant,
                meter=meter,
                ts_start=ts,
                received_at=received_at,
                obis_code=obis,
                value=value,
                unit=unit,
                is_late=is_late,
                is_duplicate=False,
                ingestion_delay_seconds=int(delay),
            )

            # Wenn verspätet eingetroffen: Sofortige Nachberechnung anstoßen
            if is_late:
                try:
                    recalculate_late_slot.delay(str(meter.id), ts.isoformat())
                except Exception:
                    pass

            written += 1

        # ✅ SUCCESS
        final_status = InboundWebhookEvent.Status.OK

        evt.status = final_status
        evt.error_message = ""
        evt.processed_at = timezone.now()
        evt.save(update_fields=["status", "error_message", "processed_at"])

        return {"status": "ok", "written": written}

    except Exception as e:
        logger.exception("event.processing.failed")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=2**self.request.retries)

        final_status = InboundWebhookEvent.Status.ERROR
        final_error = str(e)

        evt.status = final_status
        evt.error_message = final_error[:2000]
        evt.processed_at = timezone.now()
        evt.save(update_fields=["status", "error_message", "processed_at"])

        return {"status": "error"}

    finally:
        if final_status:
            try:
                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    "events",
                    {
                        "type": "send_event",
                        "data": {
                            "event_id": str(evt.id),
                            "tenant_id": str(evt.tenant_id),
                            "status": final_status,
                            "written": written,
                            "error_message": final_error,
                            "processed_at": (
                                evt.processed_at.isoformat()
                                if evt.processed_at
                                else None
                            ),
                        },
                    },
                )
            except Exception:
                logger.exception("realtime.push.failed")


############################################################
# 🔵 2. TIBBER SYNC (FINAL VERSION ✅)
############################################################


def get_hours_to_fetch(meter):
    """
    Dynamisches Fetch-Fenster:
    - kein Startwert → 72h
    - sonst delta + buffer
    """

    last = IntervalReading.objects.filter(meter=meter).order_by("-ts_start").first()

    if not last:
        return 72

    now = timezone.now()
    delta = now - last.ts_start

    hours = int(delta.total_seconds() / 3600) + 2  # buffer

    return min(max(hours, 2), 72)


@shared_task
def sync_tibber():
    """
    ✅ Stable Tibber Sync:
    - nur Meter mit tibber_home_id
    - dynamisches Zeitfenster
    - robust gegen Fehler
    """

    results = []

    meters = (
        Meter.objects.filter(integration_type="tibber")
        .exclude(tibber_home_id__isnull=True)
        .exclude(tibber_home_id="")
    )

    if not meters.exists():
        return {"status": "no_tibber_meters"}

    for meter in meters:
        user = getattr(meter, "owner_user", None)

        # ✅ HARTE VALIDIERUNG
        if not user:
            logger.warning(f"Skipping meter {meter.id} → missing owner_user")
            continue

        if not meter.tibber_home_id:
            logger.warning(f"Skipping meter {meter.id} → missing tibber_home_id")
            continue
        try:
            hours = get_hours_to_fetch(meter)

            result = upsert_tibber_interval_readings(
                meter=meter,
                home_id=meter.tibber_home_id,
                user=user,
                hours=hours,
            )

            written = result.get("written", 0)

            # ✅ optional tracking
            if written > 0:
                meter.last_tibber_sync = timezone.now()
                meter.save(update_fields=["last_tibber_sync"])

            results.append(
                {
                    "meter_id": str(meter.id),
                    "hours": hours,
                    "written": written,
                }
            )

        except Exception as e:
            logger.exception(
                f"tibber.sync.failed meter={meter.id} user={getattr(user, 'id', 'none')}"
            )
            results.append(
                {
                    "meter_id": str(meter.id),
                    "error": str(e),
                }
            )

    return {
        "status": "ok",
        "meters_processed": len(results),
        "results": results,
    }


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.Redis.from_url(REDIS_URL)

BUFFER_KEY = "mqtt:buffer"

@shared_task
def flush_mqtt_buffer():
    pipe = r.pipeline()
    pipe.lrange(BUFFER_KEY, 0, 99)
    pipe.ltrim(BUFFER_KEY, 100, -1)
    results = pipe.execute()
    items = results[0] if results else []

    if not items:
        return {"status": "empty"}

    batch = []
    for item in items:
        try:
            batch.append(json.loads(item.decode("utf-8")))
        except Exception:
            continue

    if not batch:
        return {"status": "empty"}

    device_identifiers = {
        entry.get("device_id") for entry in batch if entry.get("device_id")
    }

    devices = {
        d.identifier: d
        for d in Device.objects.filter(identifier__in=device_identifiers)
    }

    total_created = 0

    for entry in batch:
        dev_id = entry.get("device_id")
        device = devices.get(dev_id)

        if not device:
            continue

        ts = parse_datetime(entry.get("timestamp")) if entry.get("timestamp") else None
        if not ts:
            ts = timezone.now()
        elif timezone.is_naive(ts):
            ts = timezone.make_aware(ts, timezone.utc)

        # Extract metric payload (exclude routing keys)
        payload_metrics = {
            k: v for k, v in entry.items()
            if k not in ["device_id", "timestamp", "topic"]
        }
        if not payload_metrics and (entry.get("power") is not None or entry.get("value") is not None):
            val = entry.get("power") if entry.get("power") is not None else entry.get("value")
            payload_metrics = {"power": val}

        res = ingest_metric_payload(
            device=device,
            metrics=payload_metrics,
            timestamp=ts,
            source="mqtt_buffer",
            meta=entry,
        )
        total_created += res.get("created_metrics", 0)

    logger.info(
        "mqtt.buffer.flushed",
        extra={
            "batch_size": len(batch),
            "created_metrics": total_created,
        },
    )

    return {
        "status": "ok",
        "batch_size": len(batch),
        "created_metrics": total_created,
    }
    