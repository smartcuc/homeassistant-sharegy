##################
# devices/tasks.py
##################

import os
import subprocess
import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Home, Device
from .mqtt import mqtt_cmd

logger = logging.getLogger(__name__)



# ============================================================
# ✅ HELPER: SAFE COMMAND EXECUTION
# ============================================================

def run_mqtt_cmd(*args, raise_on_error=False):
    """
    Runs mosquitto_ctrl command safely.
    Logs errors but does not break provisioning unless desired.
    """

    result = subprocess.run(
        mqtt_cmd(*args),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.warning(
            "mqtt.command.failed",
            extra={
                "cmd": args,
                "stderr": result.stderr.strip(),
                "stdout": result.stdout.strip(),
            },
        )

        if raise_on_error:
            raise RuntimeError(result.stderr.strip())

    else:
        logger.debug(
            "mqtt.command.ok",
            extra={"cmd": args},
        )

    return result


# ============================================================
# ✅ PROVISION HOME (IDEMPOTENT)
# ============================================================

@shared_task(bind=True, max_retries=3)
def provision_home(self, home_id):
    try:
        home = Home.objects.get(id=home_id)

        logger.info("mqtt.provision.start", extra={"home": home.id})

        # ----------------------------------------------------
        # 1. Client
        # ----------------------------------------------------
        run_mqtt_cmd(
            "dynsec", "createClient",
            home.mqtt_username,
            "-p", home.mqtt_password,
        )

        # ----------------------------------------------------
        # 2. Role
        # ----------------------------------------------------
        run_mqtt_cmd(
            "dynsec", "createRole",
            home.mqtt_username,
        )

        # ----------------------------------------------------
        # 3. ACL: publish
        # ----------------------------------------------------
        run_mqtt_cmd(
            "dynsec", "addRoleACL",
            home.mqtt_username,
            "publishClientSend",
            f"h/{home.mqtt_token}/#",
            "allow",
        )

        # ----------------------------------------------------
        # 4. ACL: subscribe
        # ----------------------------------------------------
        run_mqtt_cmd(
            "dynsec", "addRoleACL",
            home.mqtt_username,
            "subscribePattern",
            f"h/{home.mqtt_token}/#",
            "allow",
        )

        # ----------------------------------------------------
        # 5. Role Binding
        # ----------------------------------------------------
        run_mqtt_cmd(
            "dynsec", "addClientRole",
            home.mqtt_username,
            home.mqtt_username,
        )

        # ----------------------------------------------------
        # ✅ DB Update (atomic)
        # ----------------------------------------------------
        with transaction.atomic():
            home.mqtt_provisioned = True
            home.save(update_fields=["mqtt_provisioned"])

        logger.info("mqtt.provision.success", extra={"home": home.id})

        return "OK"

    except Exception as e:
        logger.error(
            "mqtt.provision.failed",
            extra={"home": home_id, "error": str(e)},
        )
        raise self.retry(exc=e, countdown=5)


# ============================================================
# ✅ DELETE MQTT USER (ROBUST)
# ============================================================

@shared_task(bind=True, max_retries=3)
def delete_mqtt_user(self, username):
    try:
        logger.info("mqtt.delete.start", extra={"user": username})

        # ✅ delete client
        run_mqtt_cmd(
            "dynsec", "deleteClient",
            username,
        )

        # ✅ delete role (wichtig!)
        run_mqtt_cmd(
            "dynsec", "deleteRole",
            username,
        )

        logger.info("mqtt.delete.success", extra={"user": username})

    except Exception as e:
        logger.error(
            "mqtt.delete.failed",
            extra={"user": username, "error": str(e)},
        )
        raise self.retry(exc=e, countdown=5)

# ============================================================
# ✅ MONITORING
# ============================================================    
@shared_task
def mqtt_health_check():
    from django.core.management import call_command
    call_command("mqtt_monitor")


# ============================================================
# ✅AGGRIGATIONS
# ============================================================   

from celery import shared_task

from devices.services.aggregation import (
    aggregate_1m,
    aggregate_5m,
    aggregate_15m,
    aggregate_1h,
)


@shared_task
def run_1m_aggregation():
    aggregate_1m()


@shared_task
def run_5m_aggregation():
    aggregate_5m()


@shared_task
def run_15m_aggregation():
    aggregate_15m()


@shared_task
def run_1h_aggregation():
    aggregate_1h()



# ============================================================
# ✅ AUTO PURGE TRASH
# ============================================================

@shared_task
def purge_pending_devices():

    deleted, _ = Device.objects.filter(
        pending_delete=True,
        delete_after__lte=timezone.now(),
    ).delete()

    logger.info(
        "devices.purge.success",
        extra={"deleted": deleted},
    )

    return deleted


# ============================================================
# ☁️ CLOUD PROFILES POLLING TASK (SUNGROW / SOLAREDGE / FRONIUS)
# ============================================================

@shared_task(name="devices.poll_cloud_integrations")
def poll_cloud_integrations_task():
    """
    Fragt zyklisch alle aktiven Cloud-Geräte-Integrationen ab.
    """
    from devices.models import CloudDeviceIntegration
    from devices.services_profile_runner import execute_cloud_poll

    active_integrations = CloudDeviceIntegration.objects.filter(
        is_active=True,
        device__active=True,
    ).select_related("device", "device__home")

    count = 0
    errors = 0

    for integration in active_integrations:
        try:
            res = execute_cloud_poll(integration)
            if res.get("status") == "success":
                count += 1
            else:
                errors += 1
        except Exception as e:
            logger.error("Cloud poll failed for integration %s: %s", integration.id, e)
            errors += 1

    return {"polled": count, "errors": errors, "total": active_integrations.count()}


# ============================================================
# ⚡ ASYNC HIGH-THROUGHPUT TELEMETRY INGEST TASK
# ============================================================

@shared_task(name="devices.tasks.process_telemetry_push_async", bind=True, max_retries=3)
def process_telemetry_push_async(self, home_id, device_items, timestamp_str=None):
    """
    Asynchroner Celery-Worker für hochperformanten Batch-Ingest von Gerätemesswerten.
    Entkoppelt den HTTP-Endpunkt vollständig von DB-Schreibzyklen.
    """
    from django.utils.dateparse import parse_datetime
    from .models import Home, Device, DeviceConfig, DeviceRole, DeviceLatestMetric, DeviceMetric1h

    try:
        home = Home.objects.get(id=home_id)
    except Home.DoesNotExist:
        logger.warning("telemetry_push_async: Home %s does not exist.", home_id)
        return {"status": "error", "message": "Home not found"}

    now = parse_datetime(timestamp_str) if timestamp_str else timezone.now()
    if not now:
        now = timezone.now()
    elif timezone.is_naive(now):
        now = timezone.make_aware(now, timezone.utc)

    # 1. Vorhandene Geräte des Haushalts in einem einzigen Query laden
    existing_devs = {
        dev.identifier: dev
        for dev in Device.objects.filter(home=home).select_related("config")
    }

    latest_metrics_to_upsert = []
    hourly_metrics_to_upsert = []
    bucket_dt = now.replace(minute=0, second=0, microsecond=0)
    saved_count = 0
    updated_devices = []

    for item in device_items:
        identifier = str(item.get("identifier") or item.get("id") or "").strip()
        if not identifier:
            continue

        name = item.get("name") or identifier
        power_w = item.get("power_w") or item.get("power") or item.get("value")
        energy_kwh = item.get("energy_kwh") or item.get("energy")
        role_key = item.get("role") or "consumer"

        # 1. Device aus Cache oder anlegen
        dev = existing_devs.get(identifier)
        if not dev:
            dev, _ = Device.objects.get_or_create(
                home=home,
                identifier=identifier,
                defaults={
                    "configured": True,
                    "active": True,
                },
            )
            existing_devs[identifier] = dev

        # 2. Config falls nötig anlegen
        if not getattr(dev, "config", None):
            role_obj = DeviceRole.objects.filter(key=role_key).first() or DeviceRole.objects.filter(key="consumer").first()
            DeviceConfig.objects.update_or_create(
                device=dev,
                defaults={
                    "home": home,
                    "name": name,
                    "role": role_obj,
                },
            )

        # 3. Metriken sammeln & Ingestion Pipeline nutzen
        metrics_dict = {}
        if isinstance(item.get("metrics"), dict):
            metrics_dict.update(item["metrics"])
        if isinstance(item.get("data"), dict):
            metrics_dict.update(item["data"])

        for k, v in item.items():
            if k in ["identifier", "id", "name", "role", "metrics", "data", "source"]:
                continue
            if v is not None and k not in metrics_dict:
                metrics_dict[k] = v

        if metrics_dict:
            try:
                from devices.services.ingest import ingest_metric_payload
                ingest_metric_payload(
                    device=dev,
                    metrics=metrics_dict,
                    timestamp=now,
                    source="telemetry_push",
                )
                saved_count += len(metrics_dict)
            except Exception as ing_err:
                logger.warning("Error ingesting metric payload for %s: %s", identifier, ing_err)

        # 4. Stunden-Aggregat
        if power_w is not None or energy_kwh is not None:
            avg_w = float(power_w) if power_w is not None else 0.0
            energy_wh = float(energy_kwh) * 1000.0 if energy_kwh is not None else (avg_w * 1.0)
            hourly_metrics_to_upsert.append(
                DeviceMetric1h(
                    device=dev,
                    metric_key="power",
                    bucket=bucket_dt,
                    avg=avg_w,
                    min=avg_w,
                    max=avg_w,
                    count=1,
                    energy_wh=energy_wh,
                )
            )

        updated_devices.append(identifier)

    # High-Performance Batch Upserts
    if latest_metrics_to_upsert:
        DeviceLatestMetric.objects.bulk_create(
            latest_metrics_to_upsert,
            update_conflicts=True,
            unique_fields=["device", "metric_key"],
            update_fields=["value", "unit", "timestamp"],
        )

    if hourly_metrics_to_upsert:
        DeviceMetric1h.objects.bulk_create(
            hourly_metrics_to_upsert,
            update_conflicts=True,
            unique_fields=["device", "metric_key", "bucket"],
            update_fields=["avg", "min", "max", "energy_wh"],
        )

    logger.debug(
        "telemetry_push_async.success: home=%s devices=%d metrics=%d",
        home_id,
        len(updated_devices),
        saved_count,
    )

    return {
        "status": "success",
        "saved_metrics": saved_count,
        "devices_updated": updated_devices,
        "timestamp": now.isoformat(),
    }




