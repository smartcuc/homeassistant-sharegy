#####################
# alerts/services.py
#####################

from datetime import timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone

from devices.models import Device, DeviceLatestMetric
from forecast.models import WeatherForecast
from market.models import SpotPrice
from market.services_tariff import get_home_tariff, calculate_effective_price
from alerts.models import AlertEvent


def evaluate_home_alerts(home) -> list[AlertEvent]:
    """
    Führt alle 8 Erkennungsregeln für einen Haushalt aus, aktualisiert oder
    erzeugt AlertEvents und liefert alle derzeit aktiven Alarme zurück.
    """
    if not home:
        return []

    tz_name = home.timezone or "Europe/Berlin"
    tz = ZoneInfo(tz_name)
    now = timezone.now().astimezone(tz)
    hour = now.hour

    # =========================================================================
    # 1. REGEL: KEINE PV-ERZEUGUNG ERKANNT (ERTRAGSAUSFALL)
    # =========================================================================
    pv_devices = list(Device.objects.filter(
        home=home,
        active=True,
        config__role__key__in=["producer", "pv", "solar"],
    ))

    if pv_devices:
        latest_pv_w = 0.0
        for pvd in pv_devices:
            lm = DeviceLatestMetric.objects.filter(device=pvd, metric_key__in=["power", "pv_power", "value"]).first()
            if lm and lm.value is not None:
                # Wechselrichter oder Einspeisezähler übergeben Erzeugung/Einspeisung
                # je nach Zählpfeil positiv (+1074 W) oder negativ (-1074 W).
                latest_pv_w += abs(float(lm.value))

        # Sonnenzeit: Zwischen 10:00 und 17:00 Uhr
        is_daylight_peak = (10 <= hour <= 17)
        if is_daylight_peak and latest_pv_w < 50.0:
            _upsert_alert(
                home=home,
                alert_type="no_pv",
                severity=AlertEvent.SEVERITY_CRITICAL,
                title="Keine PV-Erzeugung erkannt (Ertragsausfall)",
                message=f"Die Sonne scheint ({hour:02d}:00 Uhr), aber deine Solaranlage meldet aktuell nur {latest_pv_w:.0f} W Erzeugung. Bitte Sicherungen und DC-Schalter am Wechselrichter prüfen.",
                action_hint="Wechselrichter-Status & Sicherung prüfen",
                action_type="check_inverter",
                details={"latest_pv_w": latest_pv_w, "hour": hour},
            )
        else:
            _auto_resolve_alert(home, "no_pv")

    # =========================================================================
    # 2. REGEL: BATTERIE LEER / KRITISCHER SOC
    # =========================================================================
    bat_device = Device.objects.filter(
        home=home,
        active=True,
        config__role__key__in=["battery", "storage", "akku"],
    ).first()

    if bat_device:
        lm_soc = DeviceLatestMetric.objects.filter(
            device=bat_device,
            metric_key__in=["soc", "battery_soc", "state_of_charge", "value"],
        ).first()

        current_soc = float(lm_soc.value) if (lm_soc and lm_soc.value is not None) else 50.0

        if current_soc < 10.0:
            _upsert_alert(
                home=home,
                device=bat_device,
                alert_type="battery_empty",
                severity=AlertEvent.SEVERITY_CRITICAL,
                title="Batterie leer / Notreserve erreicht",
                message=f"Der Ladestand deines Hausspeichers ist auf {current_soc:.1f} % gefallen. Der Notstrom-Tiefentladeschutz ist aktiv.",
                action_hint="Akkuladung bei günstigem Börsenstrom freigeben",
                action_type="charge_battery",
                details={"soc_pct": current_soc},
            )
        else:
            _auto_resolve_alert(home, "battery_empty")

    # =========================================================================
    # 3. REGEL: UNERWARTETER NACHTVERBRAUCH / DAUERLAST-ALARM
    # =========================================================================
    is_deep_night = (1 <= hour <= 5)
    if is_deep_night:
        load_devices = Device.objects.filter(
            home=home,
            active=True,
            config__role__key__in=["consumer", "load", "grid"],
        )
        current_load_w = 0.0
        for ld in load_devices:
            lm_load = DeviceLatestMetric.objects.filter(device=ld, metric_key__in=["power", "value"]).first()
            if lm_load and lm_load.value:
                current_load_w += float(lm_load.value)

        if current_load_w > 1200.0:
            _upsert_alert(
                home=home,
                alert_type="night_leakage",
                severity=AlertEvent.SEVERITY_WARNING,
                title="Unerwarteter Nachtverbrauch (Dauerlast)",
                message=f"Dein Haus verbraucht nachts um {hour:02d}:00 Uhr ungewöhnlich hohe {current_load_w:.0f} W Dauerlast. Mögliche Ursache: Durchlauferhitzer, Poolpumpe oder vergessener Großverbraucher.",
                action_hint="Verbraucher prüfen & abschalten",
                action_type="inspect_load",
                details={"night_load_w": current_load_w, "hour": hour},
            )
        else:
            _auto_resolve_alert(home, "night_leakage")

    # =========================================================================
    # 4. REGEL: GERÄT OFFLINE / SIGNAL-VERLUST
    # =========================================================================
    active_devices = Device.objects.filter(home=home, active=True, pending_delete=False)
    offline_threshold = now - timedelta(minutes=20)

    offline_devices = []
    for d in active_devices:
        if d.last_seen and d.last_seen < offline_threshold:
            offline_devices.append(d.config.display_name() if hasattr(d, "config") else d.identifier)

    if offline_devices:
        dev_names = ", ".join(offline_devices[:3])
        _upsert_alert(
            home=home,
            alert_type="device_offline",
            severity=AlertEvent.SEVERITY_WARNING,
            title="Gerät offline / Signal-Verlust",
            message=f"Folgende Geräte senden seit über 20 Minuten keine Telemetriedaten: {dev_names}. Bitte WLAN-Verbindung und Stromversorgung prüfen.",
            action_hint="Geräteverbindung prüfen",
            action_type="reconnect_device",
            details={"offline_devices": offline_devices},
        )
    else:
        _auto_resolve_alert(home, "device_offline")

    # =========================================================================
    # 5. REGEL: NEGATIVER STROMPREIS / BÖRSENTIEF-CHANCE
    # =========================================================================
    tariff = get_home_tariff(home, now.date())
    tariff_type = tariff.tariff_type if tariff else "dynamic"

    if tariff_type == "dynamic":
        upcoming_spots = SpotPrice.objects.filter(
            timestamp__gte=now,
            timestamp__lte=now + timedelta(hours=6),
        ).order_by("price_eur_per_kwh")

        best_spot = upcoming_spots.first()
        if best_spot:
            spot_ct = float(best_spot.price_eur_per_kwh or 0.10) * 100.0
            eff_price_ct = calculate_effective_price(home, best_spot.timestamp, spot_ct)

            if eff_price_ct <= 16.0:
                time_str = best_spot.timestamp.astimezone(tz).strftime("%H:00")
                _upsert_alert(
                    home=home,
                    alert_type="negative_price",
                    severity=AlertEvent.SEVERITY_INFO,
                    title="Börsenstrom-Tiefstpreis (Spar-Chance)",
                    message=f"Günstiger Börsenstrom um {time_str} Uhr ({eff_price_ct:.1f} ct/kWh brutto). Starte deine Wallbox oder Großverbraucher in diesem Zeitfenster.",
                    action_hint="Ladefenster im Optimizer aktivieren",
                    action_type="open_optimizer",
                    details={"best_hour": time_str, "price_ct": eff_price_ct},
                )
            else:
                _auto_resolve_alert(home, "negative_price")

    # =========================================================================
    # 6. REGEL: EXTREMER PREIS-PEAK (DUNKELFLAUTE)
    # =========================================================================
    if tariff_type == "dynamic":
        peak_spots = SpotPrice.objects.filter(
            timestamp__gte=now,
            timestamp__lte=now + timedelta(hours=4),
        ).order_by("-price_eur_per_kwh")

        highest_spot = peak_spots.first()
        if highest_spot:
            spot_ct = float(highest_spot.price_eur_per_kwh or 0.10) * 100.0
            eff_peak_ct = calculate_effective_price(home, highest_spot.timestamp, spot_ct)

            if eff_peak_ct >= 38.0:
                peak_time_str = highest_spot.timestamp.astimezone(tz).strftime("%H:00")
                _upsert_alert(
                    home=home,
                    alert_type="price_peak",
                    severity=AlertEvent.SEVERITY_WARNING,
                    title="Hohe Preisspitze an der Strombörse",
                    message=f"Um {peak_time_str} Uhr steigt der Strompreis auf {eff_peak_ct:.1f} ct/kWh. Schalte flexible Großverbraucher ab und nutze den Hausspeicher.",
                    action_hint="Großverbraucher pausieren",
                    action_type="pause_loads",
                    details={"peak_hour": peak_time_str, "price_ct": eff_peak_ct},
                )
            else:
                _auto_resolve_alert(home, "price_peak")

    # =========================================================================
    # 7. REGEL: FROSTSCHUTZ & WÄRMEPUMPEN-VORLAUF
    # =========================================================================
    cold_weather = WeatherForecast.objects.filter(
        home=home,
        ts__gte=now,
        ts__lte=now + timedelta(hours=12),
        temperature_c__lte=-5.0,
    ).first()

    if cold_weather:
        _upsert_alert(
            home=home,
            alert_type="freeze_guard",
            severity=AlertEvent.SEVERITY_INFO,
            title="Frostschutz-Wächter aktiv",
            message=f"In den nächsten 12 Stunden werden Temperaturen bis {cold_weather.temperature_c:.1f} °C erwartet. Pufferspeicher tagsüber mit Solarstrom vorheizen.",
            action_hint="Wärmepumpen-Vorlauf prüfen",
            action_type="heatpump_guard",
            details={"min_temp_c": cold_weather.temperature_c},
        )
    else:
        _auto_resolve_alert(home, "freeze_guard")

    # Aktive Alarme zurückgeben
    return list(AlertEvent.objects.filter(home=home, status__in=[AlertEvent.STATUS_ACTIVE, AlertEvent.STATUS_ACKNOWLEDGED]))


def _upsert_alert(home, alert_type, severity, title, message, action_hint="", action_type="", details=None, device=None):
    existing = AlertEvent.objects.filter(
        home=home,
        alert_type=alert_type,
        status__in=[AlertEvent.STATUS_ACTIVE, AlertEvent.STATUS_ACKNOWLEDGED],
    ).first()

    if not existing:
        event = AlertEvent.objects.create(
            home=home,
            device=device,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            action_hint=action_hint,
            action_type=action_type,
            details=details or {},
            status=AlertEvent.STATUS_ACTIVE,
        )

        try:
            from notifications.tasks import dispatch_alert_push_task
            dispatch_alert_push_task.delay(str(event.id))
        except Exception:
            # Fallback falls Celery nicht läuft / synchroner Modus
            try:
                from notifications.services import dispatch_alert_push
                dispatch_alert_push(event)
            except Exception as ex:
                import logging
                logging.getLogger(__name__).warning("Fehler beim Push-Dispatch für Alert %s: %s", event.id, str(ex))

        # Sofortige E-Mail-Warnung bei kritischen Alarmen (sofern vom Nutzer aktiviert)
        if severity == AlertEvent.SEVERITY_CRITICAL and home and getattr(home, "user", None):
            user = home.user
            user_settings = getattr(user, "settings", None)
            if user_settings is None or getattr(user_settings, "notify_critical_alerts", True):
                try:
                    from django.conf import settings
                    from accounts.services.email_service import send_critical_alert_email
                    send_critical_alert_email(
                        user=user,
                        alert_data={
                            "title": title,
                            "message": message,
                            "device_name": device.name if device else "",
                            "action_hint": action_hint,
                            "action_url": getattr(settings, "FRONTEND_URL", "https://sharegy.de") + "/alerts",
                        }
                    )
                except Exception as ex_mail:
                    import logging
                    logging.getLogger(__name__).warning("Fehler beim E-Mail-Dispatch für kritischen Alert %s: %s", event.id, str(ex_mail))

        return event
    else:
        # Bestehenden Alarm aktualisieren (Status bleibt unverändert, z. B. acknowledged bleibt in Historie)
        existing.severity = severity
        existing.title = title
        existing.message = message
        existing.action_hint = action_hint
        existing.action_type = action_type
        existing.details = details or {}
        existing.save(update_fields=["severity", "title", "message", "action_hint", "action_type", "details"])
        return existing


def _auto_resolve_alert(home, alert_type):
    AlertEvent.objects.filter(
        home=home,
        alert_type=alert_type,
        status__in=[AlertEvent.STATUS_ACTIVE, AlertEvent.STATUS_ACKNOWLEDGED],
    ).update(
        status=AlertEvent.STATUS_RESOLVED,
        resolved_at=timezone.now(),
    )


def purge_old_alerts(retention_days: int = 180) -> int:
    """
    Bereinigt automatisch Alarme aus der Datenbank, die älter als retention_days (Standard: 180 Tage / 6 Monate) sind.
    """
    cutoff = timezone.now() - timedelta(days=retention_days)
    deleted_count, _ = AlertEvent.objects.filter(created_at__lt=cutoff).delete()
    return deleted_count

