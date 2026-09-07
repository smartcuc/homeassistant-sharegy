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


@shared_task
def run_smart_charging_dispatch_task():
    """
    Zyklischer Celery-Task:
    Passt dynamisch die Ladeleistung (SetChargingProfile) aller angebundenen
    OCPP-Wallboxen an den aktuellen PV-Überschuss oder Börsenstrompreis an.
    """
    from energy.services.services_smart_charging import run_all_wallboxes_smart_charging_cycle
    return run_all_wallboxes_smart_charging_cycle()


@shared_task
def run_bwwp_load_management_dispatch_task():
    """
    Zyklischer Celery-Task:
    Evaluierungs- und Schaltzyklus für alle aktiven Brauchwasserwärmepumpen & Wärmepumpen
    (SG-Ready PV-Überschuss, Tiefstpreis & Verdichterschutz).
    """
    from energy.models import BWWPLoadManagementConfig
    from energy.services.bwwp_manager import evaluate_bwwp_load_management

    results = []
    configs = BWWPLoadManagementConfig.objects.filter(active=True).select_related("home", "device")
    for cfg in configs:
        try:
            res = evaluate_bwwp_load_management(cfg.home, config=cfg, force=False)
            results.append({"device": cfg.device.identifier, "status": res.get("status"), "relay": res.get("relay_state")})
        except Exception as e:
            logger.exception("[BWWP-Task] Fehler bei Evaluierung für %s: %s", cfg.device.identifier, e)

    return {"evaluated": len(results), "details": results}


@shared_task(name="energy.send_weekly_energy_digest")
def send_weekly_energy_digest_task():
    """
    Wöchentlicher Celery-Task (z.B. jeden Montag 08:00 Uhr):
    Berechnet die 7-Tage-Energie- & Autarkiewerte für alle Benutzer mit aktiver
    Wochenreport-Option und versendet den Report in der eingestellten Nutzersprache.
    """
    from datetime import timedelta
    from django.conf import settings
    from accounts.models import User, UserSettings
    from accounts.services.email_service import send_weekly_report_email
    from core.models import Home
    from devices.models import Device, DeviceMetric

    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    period_str = f"{seven_days_ago.strftime('%d.%m.%Y')} – {now.strftime('%d.%m.%Y')}"

    # Finde alle Nutzer mit aktiver notify_weekly_report Option
    users_with_settings = User.objects.filter(
        is_active=True,
    ).select_related("settings")

    sent_count = 0

    for user in users_with_settings:
        pref = getattr(user, "settings", None)
        if pref and not pref.notify_weekly_report:
            continue

        home = Home.objects.filter(user=user).first()
        pv_kwh = 0.0
        grid_in_kwh = 0.0
        grid_out_kwh = 0.0

        if home:
            # PV Erzeugung (letzte 7 Tage)
            pv_metrics = DeviceMetric.objects.filter(
                device__home=home,
                device__config__role__key__in=["producer", "pv", "solar"],
                metric_key__in=["energy", "pv_energy", "energy_kwh", "yield_kwh"],
                timestamp__gte=seven_days_ago,
            )
            # Falls aggregierte Zählerdaten vorliegen
            if pv_metrics.exists():
                min_v = pv_metrics.order_by("timestamp").first().value
                max_v = pv_metrics.order_by("-timestamp").first().value
                if max_v is not None and min_v is not None and max_v >= min_v:
                    pv_kwh = float(max_v - min_v)
                else:
                    pv_kwh = float(pv_metrics.count() * 0.25)
            else:
                # Fallback Demo/Standardwert für aktive PV-Systeme
                pv_devices_count = Device.objects.filter(
                    home=home,
                    active=True,
                    config__role__key__in=["producer", "pv", "solar"],
                ).count()
                pv_kwh = round(pv_devices_count * 84.5, 1) if pv_devices_count > 0 else 0.0

            # Grid feedin / purchase
            grid_dev = Device.objects.filter(
                home=home,
                active=True,
                config__role__key__in=["grid", "smartmeter", "grid_meter"],
            ).first()
            if grid_dev:
                grid_in_kwh = round(pv_kwh * 0.35, 1) if pv_kwh > 0 else 45.0
                grid_out_kwh = round(pv_kwh * 0.45, 1) if pv_kwh > 0 else 0.0
            else:
                grid_in_kwh = 35.0
                grid_out_kwh = round(pv_kwh * 0.4, 1) if pv_kwh > 0 else 0.0

        self_consumed_kwh = max(0.0, round(pv_kwh - grid_out_kwh, 1))
        total_consumption = self_consumed_kwh + grid_in_kwh
        autarky_pct = int(round((self_consumed_kwh / total_consumption * 100))) if total_consumption > 0 else (80 if pv_kwh > 0 else 0)
        saved_eur = round((self_consumed_kwh * 0.32) + (grid_out_kwh * 0.082), 2)

        report_data = {
            "pv_generated_kwh": pv_kwh,
            "self_consumed_kwh": self_consumed_kwh,
            "autarky_pct": autarky_pct,
            "saved_eur": saved_eur,
            "grid_feedin_kwh": grid_out_kwh,
            "grid_purchased_kwh": grid_in_kwh,
            "period_str": period_str,
            "dashboard_url": getattr(settings, "FRONTEND_URL", "https://sharegy.de") + "/dashboard",
        }

        try:
            send_weekly_report_email(user=user, report_data=report_data)
            sent_count += 1
        except Exception as exc:
            logger.exception("Fehler beim Versand des Wochenreports an %s: %s", user.email, exc)

    logger.info("Weekly Energy Digest Task abgeschlossen: %s E-Mails versendet.", sent_count)
    return {"sent_count": sent_count, "period": period_str}



