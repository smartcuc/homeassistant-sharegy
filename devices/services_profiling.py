import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Min, Max

from devices.models import Device, DeviceMetric, DeviceBaselineProfile
from alerts.models import AlertEvent

logger = logging.getLogger(__name__)

APPLIANCE_PRESETS = {
    "bwwp": {
        "label": "Brauchwasserwärmepumpe (BWWP)",
        "standby_power_w": 30.0,
        "standby_tolerance_pct": 30.0,
        "standby_max_w": 45.0,
        "operating_power_min_w": 350.0,
        "operating_power_max_w": 750.0,
        "max_continuous_run_hours": 6.0,
        "description": "Überwacht Standby (30W) und Kompressorbetrieb (ca. 500W). Erkennt Verschleiß, Dauerlauf und erhöhten Ruhestrom.",
    },
    "heatpump": {
        "label": "Heizungs-Wärmepumpe",
        "standby_power_w": 45.0,
        "standby_tolerance_pct": 30.0,
        "standby_max_w": 65.0,
        "operating_power_min_w": 600.0,
        "operating_power_max_w": 4000.0,
        "max_continuous_run_hours": 12.0,
        "description": "Erkennt Taktungsanomalien, Vereisung des Außengeräts und fehlerhaftes Heizstab-Zuschalten.",
    },
    "fridge": {
        "label": "Kühlschrank / Gefriergerät",
        "standby_power_w": 2.0,
        "standby_tolerance_pct": 50.0,
        "standby_max_w": 6.0,
        "operating_power_min_w": 35.0,
        "operating_power_max_w": 180.0,
        "max_continuous_run_hours": 2.5,
        "description": "Erkennt offene Türen, defekte Dichtungen, Kompressor-Dauerlauf und Kriechstrom.",
    },
    "circulation_pump": {
        "label": "Zirkulationspumpe",
        "standby_power_w": 0.5,
        "standby_tolerance_pct": 100.0,
        "standby_max_w": 2.0,
        "operating_power_min_w": 10.0,
        "operating_power_max_w": 50.0,
        "max_continuous_run_hours": 1.0,
        "description": "Erkennt Dauerlauf und defekte Zeitschaltuhren/Sensoren.",
    },
    "heating_pump": {
        "label": "Umwälz- / Heizungspumpe",
        "standby_power_w": 2.0,
        "standby_tolerance_pct": 50.0,
        "standby_max_w": 5.0,
        "operating_power_min_w": 10.0,
        "operating_power_max_w": 60.0,
        "max_continuous_run_hours": 24.0,
        "description": "Überwacht hydraulischen Abgleich und Leistungsaufnahme der Heizkreispumpe.",
    },
    "generic": {
        "label": "Individuelles Gerät",
        "standby_power_w": 10.0,
        "standby_tolerance_pct": 40.0,
        "standby_max_w": 25.0,
        "operating_power_min_w": 100.0,
        "operating_power_max_w": 2000.0,
        "max_continuous_run_hours": 8.0,
        "description": "Frei konfigurierbare Grenzwerte und Baseline-Überwachung.",
    },
}


def get_or_create_device_profile(device: Device, appliance_type: str = "generic") -> DeviceBaselineProfile:
    """
    Liefert das Baseline-Profil für ein Gerät oder initialisiert es mit Standard-Preset.
    """
    preset = APPLIANCE_PRESETS.get(appliance_type, APPLIANCE_PRESETS["generic"])
    profile, created = DeviceBaselineProfile.objects.get_or_create(
        device=device,
        defaults={
            "appliance_type": appliance_type,
            "standby_power_w": preset["standby_power_w"],
            "standby_tolerance_pct": preset["standby_tolerance_pct"],
            "standby_max_w": preset["standby_max_w"],
            "operating_power_min_w": preset["operating_power_min_w"],
            "operating_power_max_w": preset["operating_power_max_w"],
            "max_continuous_run_hours": preset["max_continuous_run_hours"],
        },
    )
    return profile


def learn_device_baseline(device: Device, days: int = 7) -> DeviceBaselineProfile:
    """
    Analysiert historische Leistungsmesswerte der letzten N Tage und lernt
    die Ruhe-Baseline und Betriebsleistung automatisch.
    """
    profile = get_or_create_device_profile(device)
    cutoff = timezone.now() - timedelta(days=days)

    power_metrics = DeviceMetric.objects.filter(
        device=device,
        metric_key__in=["power", "apower", "power_w"],
        timestamp__gte=cutoff,
    ).values_list("value", flat=True)

    values = [float(v) for v in power_metrics if v is not None and float(v) >= 0]
    if not values:
        logger.info("[Baseline-Learning] Keine ausreichenden Messwerte für Gerät %s", device.identifier)
        return profile

    values.sort()
    count = len(values)

    # 1. Standby = 10%-Quantil der niedrigsten Werte
    p10_idx = int(count * 0.10)
    standby_est = round(values[p10_idx], 1)

    # 2. Standby-Obergrenze = Standby + 40% (mindestens +10W)
    standby_max_est = round(max(standby_est * 1.4, standby_est + 10.0), 1)

    # 3. Betriebsleistung = 90%-Quantil
    p90_idx = int(count * 0.90)
    operating_est = round(values[p90_idx], 1)

    profile.standby_power_w = standby_est
    profile.standby_max_w = standby_max_est
    if operating_est > standby_max_est:
        profile.operating_power_min_w = round(standby_max_est * 1.5, 1)
        profile.operating_power_max_w = round(operating_est * 1.3, 1)

    profile.learning_mode = False
    profile.save()
    logger.info(
        "[Baseline-Learning] ✅ Baseline für %s gelernt: Standby=%s W (Max=%s W), Betrieb=%s-%s W",
        device.identifier,
        profile.standby_power_w,
        profile.standby_max_w,
        profile.operating_power_min_w,
        profile.operating_power_max_w,
    )
    return profile


def evaluate_device_baseline(device: Device) -> dict:
    """
    Bewertet den aktuellen Zustand des Geräts gegen seine Baseline.
    Generiert bei Abweichungen (z. B. Standby 50W statt 30W) automatisch einen Alert in der Alarmzentrale.
    """
    profile = getattr(device, "baseline_profile", None)
    if not profile or not profile.is_active:
        return {"status": "inactive", "message": "Baseline-Überwachung nicht aktiv"}

    now = timezone.now()
    # 1. Letzte 15 Minuten Messwerte betrachten
    recent_metrics = DeviceMetric.objects.filter(
        device=device,
        metric_key__in=["power", "apower", "power_w"],
        timestamp__gte=now - timedelta(minutes=15),
    ).aggregate(avg_power=Avg("value"), max_power=Max("value"), min_power=Min("value"))

    avg_power = recent_metrics["avg_power"]
    if avg_power is None:
        return {"status": "no_data", "message": "Keine aktuellen Messwerte verfügbar"}

    avg_power = float(avg_power)
    dev_name = getattr(device, "name", None) or getattr(device, "custom_name", None) or device.identifier


    # =========================================================================
    # A) PRÜFUNG: ERHÖHTER STANDBY- / RUHEVERBRAUCH (z. B. 50W statt 30W)
    # =========================================================================
    # Wenn die Leistung im Bereich zwischen Standby-Max und Betriebs-Minimum liegt
    # ODER wenn die Leistung deutlich über dem Standby liegt, aber kein voller Betrieb ist:
    if profile.standby_max_w < avg_power < profile.operating_power_min_w:
        status = DeviceBaselineProfile.HEALTH_ANOMALY
        pct_increase = int(((avg_power - profile.standby_power_w) / max(profile.standby_power_w, 1.0)) * 100)
        reason = (
            f"Standby-Verbrauch liegt mit {avg_power:.1f} W um {pct_increase}% über der Baseline "
            f"({profile.standby_power_w:.1f} W, Grenzwert: {profile.standby_max_w:.1f} W). "
            f"Mögliche Ursache: Sensorfehler, verändertes Regelverhalten, Verkalkung oder Kriechstrom."
        )

        profile.current_health_status = status
        profile.last_measured_standby_w = round(avg_power, 1)
        profile.anomaly_reason = reason
        profile.save()

        # 🚨 Alert in Alarmzentrale generieren (mit Duplikatschutz)
        existing_alert = AlertEvent.objects.filter(
            home=device.home,
            device=device,
            alert_type="custom",
            status=AlertEvent.STATUS_ACTIVE,
            title__contains="Geräteanomalie (Standby-Erhöhung)",
        ).first()

        if not existing_alert:
            AlertEvent.objects.create(
                home=device.home,
                device=device,
                alert_type="custom",
                severity=AlertEvent.SEVERITY_WARNING,
                title=f"⚠️ Geräteanomalie (Standby-Erhöhung): {dev_name}",
                message=reason,
                details={
                    "anomaly_type": "elevated_standby",
                    "measured_avg_w": round(avg_power, 1),
                    "baseline_standby_w": profile.standby_power_w,
                    "threshold_max_w": profile.standby_max_w,
                    "appliance_type": profile.appliance_type,
                },
            )
            logger.warning("[Baseline-Watchdog] 🚨 Alert ausgelöst für %s: %s", dev_name, reason)

        return {"status": status, "reason": reason, "measured_w": avg_power}

    # =========================================================================
    # B) PRÜFUNG: DAUERLAUF-ANOMALIE (Kompressor läuft zu lange ohne Pause)
    # =========================================================================
    if avg_power >= profile.operating_power_min_w and profile.max_continuous_run_hours > 0:
        run_cutoff = now - timedelta(hours=profile.max_continuous_run_hours)
        min_in_window = DeviceMetric.objects.filter(
            device=device,
            metric_key__in=["power", "apower", "power_w"],
            timestamp__gte=run_cutoff,
        ).aggregate(min_val=Min("value"))["min_val"]

        # Wenn der Minimalwert im Zeitfenster nie unter das Standby-Niveau gefallen ist -> Dauerlauf!
        if min_in_window is not None and float(min_in_window) >= profile.operating_power_min_w:
            status = DeviceBaselineProfile.HEALTH_ANOMALY
            reason = (
                f"Ungewöhnlicher Dauerbetrieb: {dev_name} läuft seit über {profile.max_continuous_run_hours:.1f} Stunden "
                f"ununterbrochen im Betriebsmodus (Leistung: {avg_power:.1f} W). "
                f"Mögliche Ursache: Wärmeverlust, Vereisung, Kältemittelmangel oder Thermostat-Defekt."
            )
            profile.current_health_status = status
            profile.last_measured_operating_w = round(avg_power, 1)
            profile.anomaly_reason = reason
            profile.save()

            existing_run_alert = AlertEvent.objects.filter(
                home=device.home,
                device=device,
                alert_type="custom",
                status=AlertEvent.STATUS_ACTIVE,
                title__contains="Dauerbetriebs-Anomalie",
            ).first()

            if not existing_run_alert:
                AlertEvent.objects.create(
                    home=device.home,
                    device=device,
                    alert_type="custom",
                    severity=AlertEvent.SEVERITY_CRITICAL,
                    title=f"🚨 Dauerbetriebs-Anomalie: {dev_name}",
                    message=reason,
                    details={
                        "anomaly_type": "continuous_run",
                        "measured_avg_w": round(avg_power, 1),
                        "max_hours": profile.max_continuous_run_hours,
                        "appliance_type": profile.appliance_type,
                    },
                )
            return {"status": status, "reason": reason, "measured_w": avg_power}

    # =========================================================================
    # C) ALLES NORMAL / BASELINE EINGEHALTEN
    # =========================================================================
    profile.current_health_status = DeviceBaselineProfile.HEALTH_HEALTHY
    profile.anomaly_reason = ""
    if avg_power <= profile.standby_max_w:
        profile.last_measured_standby_w = round(avg_power, 1)
    else:
        profile.last_measured_operating_w = round(avg_power, 1)
    profile.save()

    # Vorherige Alerts für dieses Gerät auflösen
    AlertEvent.objects.filter(
        home=device.home,
        device=device,
        alert_type="custom",
        status=AlertEvent.STATUS_ACTIVE,
        title__contains="Geräteanomalie",
    ).update(status=AlertEvent.STATUS_RESOLVED)

    return {
        "status": DeviceBaselineProfile.HEALTH_HEALTHY,
        "message": f"Baseline eingehalten ({avg_power:.1f} W)",
        "measured_w": avg_power,
    }


def evaluate_all_device_baselines():
    """
    Wird periodisch (z. B. durch Celery / Ingest) aufgerufen, um alle aktiven Baseline-Profile zu prüfen.
    """
    profiles = DeviceBaselineProfile.objects.filter(is_active=True).select_related("device", "device__home")
    evaluated_count = 0
    anomalies_count = 0

    for prof in profiles:
        try:
            res = evaluate_device_baseline(prof.device)
            evaluated_count += 1
            if res.get("status") == DeviceBaselineProfile.HEALTH_ANOMALY:
                anomalies_count += 1
        except Exception:
            logger.exception("Fehler bei Baseline-Prüfung für Gerät #%s", prof.device_id)

    return {"evaluated": evaluated_count, "anomalies": anomalies_count}
