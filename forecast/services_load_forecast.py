#####################################
# forecast/services_load_forecast.py
#####################################

from datetime import timedelta
from collections import defaultdict
from zoneinfo import ZoneInfo
from django.utils import timezone
from django.db.models import Avg

from devices.models import Device, DeviceMetric1h
from forecast.models import WeatherForecast, SolarForecast


# Standard-Lastprofil H0 (Haushalt, normiert auf 1.0 kW Tagesmittel)
# Index 0 = 00:00 Uhr bis 23 = 23:00 Uhr
H0_WORKDAY_PROFILE = [
    0.38, 0.32, 0.28, 0.26, 0.29, 0.42,
    0.68, 0.85, 0.72, 0.60, 0.58, 0.75,
    0.88, 0.70, 0.58, 0.62, 0.74, 0.95,
    1.15, 1.22, 1.10, 0.92, 0.68, 0.48,
]

H0_WEEKEND_PROFILE = [
    0.42, 0.35, 0.30, 0.28, 0.29, 0.34,
    0.45, 0.62, 0.85, 0.98, 1.05, 1.12,
    1.08, 0.92, 0.82, 0.85, 0.92, 1.05,
    1.18, 1.25, 1.12, 0.95, 0.72, 0.52,
]


def get_household_load_forecast(user, horizon_hours: int = 48) -> dict:
    """
    Berechnet die vorausschauende 24h/48h Haushalts-Verbrauchsprognose
    kombiniert mit dem PV-Ertrag und ermittelt den echten Netto-Solarüberschuss.
    """
    home = user.homes.first() if hasattr(user, "homes") else None
    tz_name = home.timezone if home and home.timezone else "Europe/Berlin"
    tz = ZoneInfo(tz_name)

    now = timezone.now().astimezone(tz)
    start_hour = now.replace(minute=0, second=0, microsecond=0)
    end_hour = start_hour + timedelta(hours=horizon_hours)

    has_devices = bool(home and Device.objects.filter(home=home, active=True).exists())
    has_generators = bool(home and home.generator_systems.exists())

    if not has_devices and not has_generators:
        return {
            "horizon_hours": horizon_hours,
            "has_custom_history": False,
            "has_heatpump": False,
            "has_pv": False,
            "has_devices": False,
            "kpis": {
                "total_load_kwh": 0.0,
                "total_pv_kwh": 0.0,
                "total_surplus_kwh": 0.0,
                "total_grid_import_kwh": 0.0,
                "total_self_consumption_kwh": 0.0,
                "autarky_pct": 0.0,
                "self_consumption_rate_pct": 0.0,
                "peak_load_kw": 0.0,
                "peak_load_time": "-",
                "peak_pv_kw": 0.0,
                "peak_pv_time": "-",
                "peak_surplus_kw": 0.0,
                "peak_surplus_time": "-",
            },
            "timeline": [],
        }

    # 1. Historische Lastprofile aus DeviceMetric1h laden (letzte 30 Tage)
    historical_hourly = defaultdict(lambda: {"sum": 0.0, "count": 0})
    has_custom_history = False

    if home:
        history_start = start_hour - timedelta(days=30)
        # Alle Last- / Verbrauchsgeräte des Haushalts
        load_device_ids = list(
            Device.objects.filter(
                home=home,
                active=True,
                config__role__key__in=["consumer", "load", "grid", "wallbox", "heatpump"],
            ).values_list("id", flat=True)
        )

        if load_device_ids:
            history_qs = (
                DeviceMetric1h.objects.filter(
                    device_id__in=load_device_ids,
                    metric_key__in=["power", "value", "power_w"],
                    bucket__gte=history_start,
                    bucket__lt=start_hour,
                )
                .values("bucket")
                .annotate(avg_w=Avg("avg"))
            )

            for row in history_qs:
                dt_loc = row["bucket"].astimezone(tz)
                weekday = dt_loc.weekday()  # 0=Mo, 6=So
                is_wknd = 1 if weekday >= 5 else 0
                hour = dt_loc.hour
                val_kw = float(row["avg_w"] or 0) / 1000.0
                if val_kw > 0:
                    historical_hourly[(is_wknd, hour)]["sum"] += val_kw
                    historical_hourly[(is_wknd, hour)]["count"] += 1
                    has_custom_history = True

    # 2. Prüfen ob Wärmepumpe vorhanden ist (für Temperaturkompensation)
    has_heatpump = False
    has_pv = False
    if home:
        has_heatpump = Device.objects.filter(
            home=home,
            active=True,
            config__role__key__in=["heatpump", "heating"],
        ).exists()
        has_pv = Device.objects.filter(
            home=home,
            active=True,
            config__role__key__in=["producer", "pv", "solar"],
        ).exists()

    # 3. Wetter- & Temperaturprognose laden
    weather_map = {}
    if home:
        w_qs = WeatherForecast.objects.filter(
            home=home,
            ts__gte=start_hour - timedelta(hours=1),
            ts__lte=end_hour + timedelta(hours=1),
        ).values("ts", "temperature_c")

        for w in w_qs:
            ts_loc = w["ts"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
            if w["temperature_c"] is not None:
                weather_map[ts_loc] = float(w["temperature_c"])

    # 4. PV-Forecast laden
    pv_forecast_map = defaultdict(float)
    if home:
        for generator in home.generator_systems.all():
            for string in generator.strings.all():
                f_qs = SolarForecast.objects.filter(
                    generator_string=string,
                    timestamp__gte=start_hour,
                    timestamp__lte=end_hour,
                ).values("timestamp", "forecast_kwh")
                for row in f_qs:
                    ts_loc = row["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
                    pv_forecast_map[ts_loc] += float(row["forecast_kwh"] or 0)

    # 5. Timeline für die nächsten horizon_hours aufbauen
    timeline = []
    total_load_kwh = 0.0
    total_pv_kwh = 0.0
    total_surplus_kwh = 0.0
    total_grid_import_kwh = 0.0
    total_self_consumption_kwh = 0.0

    for i in range(horizon_hours):
        slot_dt = start_hour + timedelta(hours=i)
        hour = slot_dt.hour
        is_wknd = 1 if slot_dt.weekday() >= 5 else 0

        # A. Basislast ermitteln
        if has_custom_history and historical_hourly[(is_wknd, hour)]["count"] >= 3:
            h_data = historical_hourly[(is_wknd, hour)]
            base_kw = h_data["sum"] / h_data["count"]
        else:
            profile = H0_WEEKEND_PROFILE if is_wknd else H0_WORKDAY_PROFILE
            # Normiert auf typischen Haushalt mit 0.5 kW Durchschnitts-Grundlast (~4.380 kWh/a)
            base_kw = profile[hour] * 0.55

        # B. Temperatur-Kompensation (Heizgradtage / Wärmepumpe / Klima)
        temp_c = weather_map.get(slot_dt, 16.5)
        temp_adj_kw = 0.0
        if temp_c < 15.0:
            delta_t = 15.0 - temp_c
            # Basis-Zuschlag für Heizung/Zirkulationspumpen
            temp_adj_kw += delta_t * 0.025
            if has_heatpump:
                # Zusätzlicher Wärmepumpen-Strombedarf bei Kälte
                temp_adj_kw += delta_t * 0.12
        elif temp_c > 26.0:
            delta_t = temp_c - 26.0
            # Klimatisierungs-Zuschlag
            temp_adj_kw += delta_t * 0.06

        total_slot_load_kw = round(max(0.15, base_kw + temp_adj_kw), 3)

        # C. PV-Leistung für den Slot
        pv_kw = round(pv_forecast_map.get(slot_dt, 0.0), 3)

        # D. Netto-Bilanzen
        net_surplus_kw = round(max(0.0, pv_kw - total_slot_load_kw), 3)
        net_grid_import_kw = round(max(0.0, total_slot_load_kw - pv_kw), 3)
        self_cons_kw = round(min(pv_kw, total_slot_load_kw), 3)

        # Aggregationen (1 Stunde = 1 kWh pro kW Leistung)
        total_load_kwh += total_slot_load_kw
        total_pv_kwh += pv_kw
        total_surplus_kwh += net_surplus_kw
        total_grid_import_kwh += net_grid_import_kw
        total_self_consumption_kwh += self_cons_kw

        weekday_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

        timeline.append({
            "timestamp": slot_dt.isoformat(),
            "time_label": slot_dt.strftime("%H:00"),
            "date_label": slot_dt.strftime("%d.%m."),
            "weekday_label": weekday_names[slot_dt.weekday()],
            "hour": hour,
            "is_weekend": bool(is_wknd),
            "temperature_c": round(temp_c, 1),
            "baseline_load_kw": round(base_kw, 2),
            "temp_adjustment_kw": round(temp_adj_kw, 2),
            "total_load_kw": round(total_slot_load_kw, 2),
            "pv_forecast_kw": round(pv_kw, 2),
            "net_surplus_kw": round(net_surplus_kw, 2),
            "net_grid_import_kw": round(net_grid_import_kw, 2),
            "self_consumption_kw": round(self_cons_kw, 2),
            "has_surplus": net_surplus_kw > 0.05,
        })

    # Autarkiegrad und Eigenverbrauchsquote
    autarky_pct = round((total_self_consumption_kwh / max(0.001, total_load_kwh)) * 100.0, 1)
    self_cons_pct = round((total_self_consumption_kwh / max(0.001, total_pv_kwh)) * 100.0, 1)

    peak_load_slot = max(timeline, key=lambda x: x["total_load_kw"]) if timeline else None
    peak_pv_slot = max(timeline, key=lambda x: x["pv_forecast_kw"]) if timeline else None
    peak_surplus_slot = max(timeline, key=lambda x: x["net_surplus_kw"]) if timeline else None

    return {
        "horizon_hours": horizon_hours,
        "has_custom_history": has_custom_history,
        "has_heatpump": has_heatpump,
        "has_pv": has_pv,
        "kpis": {
            "total_load_kwh": round(total_load_kwh, 2),
            "total_pv_kwh": round(total_pv_kwh, 2),
            "total_surplus_kwh": round(total_surplus_kwh, 2),
            "total_grid_import_kwh": round(total_grid_import_kwh, 2),
            "total_self_consumption_kwh": round(total_self_consumption_kwh, 2),
            "autarky_pct": min(100.0, autarky_pct),
            "self_consumption_rate_pct": min(100.0, self_cons_pct),
            "peak_load_kw": peak_load_slot["total_load_kw"] if peak_load_slot else 0.0,
            "peak_load_time": f"{peak_load_slot['date_label']} {peak_load_slot['time_label']}" if peak_load_slot else "",
            "peak_pv_kw": peak_pv_slot["pv_forecast_kw"] if peak_pv_slot else 0.0,
            "peak_pv_time": f"{peak_pv_slot['date_label']} {peak_pv_slot['time_label']}" if peak_pv_slot else "",
            "peak_surplus_kw": peak_surplus_slot["net_surplus_kw"] if peak_surplus_slot else 0.0,
            "peak_surplus_time": f"{peak_surplus_slot['date_label']} {peak_surplus_slot['time_label']}" if peak_surplus_slot else "",
        },
        "timeline": timeline,
    }

