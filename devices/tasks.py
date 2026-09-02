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


