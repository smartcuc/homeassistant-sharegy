#################
# energy/tasks.py
#################


import logging
from django.db import transaction
from django.utils import timezone
from celery import shared_task

#from energy.models import DeviceCommand
from energy.mqtt_publisher import MqttPublisher

logger = logging.getLogger("energy.command_publisher")


def device_command_topic(device):
    # device.device_type und device.name (dein device_id) sind bereits im Device Modell
    return f"energy/{device.device_type}/{device.name}/command"


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def publish_pending_device_commands(self, batch_size: int = 25):
    """
    Nimmt queued Commands aus der DB und published via MQTT.
    Idempotent: setzt status -> sent.
    Retry: Celery retry bei MQTT Fehler.
    """
    pub = MqttPublisher()
    sent = 0

    while sent < batch_size:
        with transaction.atomic():
            cmd = (
                DeviceCommand.objects.select_for_update(skip_locked=True)
                .filter(status="queued")
                .order_by("ts_created")
                .first()
            )

            if not cmd:
                break

            topic = device_command_topic(cmd.device)
            payload = {
                "ts": timezone.now().isoformat().replace("+00:00", "Z"),
                "command_id": str(cmd.id),
                "command": cmd.command,
                "payload": cmd.payload,
            }

            try:
                pub.publish_json(topic, payload, qos=1, retain=False)
                cmd.status = "sent"
                cmd.ts_sent = timezone.now()
                cmd.attempts = cmd.attempts + 1
                cmd.last_error = ""
                cmd.save(update_fields=["status", "ts_sent", "attempts", "last_error"])
                sent += 1
            except Exception as e:
                cmd.attempts = cmd.attempts + 1
                cmd.status = "failed" if cmd.attempts >= 3 else "queued"
                cmd.last_error = str(e)
                cmd.save(update_fields=["attempts", "status", "last_error"])
                logger.exception("publish failed command_id=%s topic=%s", cmd.id, topic)
                # Celery retry (optional)
                raise self.retry(exc=e)

    return {"published": sent}


@shared_task
def run_battery_arbitrage_dispatch_task():
    """
    Zyklischer Celery-Task:
    Führt für alle aktiven Speicher im Modus 'price_optimized' die automatische
    Arbitrage-Steuerung (Netzladung bei Tiefstpreisen / Rückstellung auf PV-Autarkie) durch.
    """
    from producer.services_dispatch import dispatch_all_storage_systems
    return dispatch_all_storage_systems()

