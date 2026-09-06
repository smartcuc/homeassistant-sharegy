############################
# energy/services/balance.py
############################

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone
from collections import defaultdict

from devices.models import Device, DeviceMetric1h
from market.models_tariff import HomeTariff
from market.services_tariff import get_home_tariff, calculate_effective_price
from market.models import SpotPrice


def get_device_name(dev):
    cfg = getattr(dev, "config", None)
    if cfg and cfg.name:
        return cfg.name
    return getattr(dev, "display_name", None) or dev.identifier


def get_consumer_icon_and_category(device_name, role_key):
    name_lower = (device_name or "").lower()
    if any(k in name_lower for k in ["wallbox", "easee", "ev", "auto", "ladestation", "charger"]):
        return "🚗", "mobility"
    elif any(k in name_lower for k in ["wärmepumpe", "heatpump", "heizung", "klima", "hvac"]):
        return "♨️", "heating"
    elif any(k in name_lower for k in ["küche", "kühlschrank", "herd", "geschirrspüler", "backofen"]):
        return "🍳", "kitchen"
    elif any(k in name_lower for k in ["waschmaschine", "trockner", "laundry", "washing"]):
        return "🧺", "laundry"
    elif any(k in name_lower for k in ["server", "pc", "it", "router", "büro"]):
        return "💻", "it"
    elif any(k in name_lower for k in ["licht", "beleuchtung", "light"]):
        return "💡", "lighting"
    elif role_key == "consumer":
        return "⚡", "consumer"
    return "🔌", "device"


def get_period_range(period_str, tz, start_date=None, end_date=None):
    now = timezone.now().astimezone(tz)

    if period_str == "custom" and start_date:
        try:
            if isinstance(start_date, str):
                if "T" in start_date:
                    start_dt = datetime.fromisoformat(start_date)
                else:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                if timezone.is_naive(start_dt):
                    start_dt = start_dt.replace(tzinfo=tz)
            else:
                start_dt = start_date

            if end_date:
                if isinstance(end_date, str):
                    if "T" in end_date:
                        end_dt = datetime.fromisoformat(end_date)
                    else:
                        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                    if timezone.is_naive(end_dt):
                        end_dt = end_dt.replace(tzinfo=tz)
                else:
                    end_dt = end_date
            else:
                end_dt = now

            duration_days = (end_dt - start_dt).days
            label = f"{start_dt.strftime('%d.%m.%Y')} - {end_dt.strftime('%d.%m.%Y')}"

            if duration_days <= 1:
                bucket_format = "%H:00"
            elif duration_days <= 3:
                bucket_format = "%d.%m. %H:00"
            elif duration_days <= 60:
                bucket_format = "%d.%m."
            else:
                bucket_format = "%b %Y"

            return start_dt, end_dt, label, bucket_format
        except Exception:
            pass

    if period_str == "7d":
        start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        label = "Letzte 7 Tage"
        bucket_format = "%d.%m."
    elif period_str == "30d":
        start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        label = "Letzte 30 Tage"
        bucket_format = "%d.%m."
    elif period_str == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        label = f"Jahr {now.year}"
        bucket_format = "%b"
    else:  # "today"
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        label = "Heute"
        bucket_format = "%H:00"

    end = now
    return start, end, label, bucket_format


def get_energy_balance(user, period="today", start_date=None, end_date=None) -> dict:
    """
    Berechnet die umfassende Energie-, Mengen-, Kosten- und Verbrauchsbilanz
    inklusive Sub-Metering (virtuelle Zähler), Residual-Zähler und zeitfenstergenauer
    Tarifbewertung (Festpreis vs. dynamischer EPEX Spot Marktpreis & EEG Einspeisesatz).
    Unterstützt freie Zeiträume via period='custom', start_date & end_date.
    """
    home = user.homes.first() if hasattr(user, "homes") else None
    tz_name = home.timezone if home and home.timezone else "Europe/Berlin"
    tz = ZoneInfo(tz_name)

    start_dt, end_dt, period_label, bucket_format = get_period_range(period, tz, start_date=start_date, end_date=end_date)
    now_dt = timezone.now().astimezone(tz)
    now = now_dt

    # 1. Alle Geräte des Nutzers laden
    devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        ).select_related("config__role", "config__energy_signal_type", "config__metric_definition")
    )

    # 1. EMS Signal Sources laden (höchste Priorität für die Zuordnung)
    from energy.ems.models import EMSSignalSource
    from devices.models import DeviceMetric15m, DeviceMetric, DeviceLatestMetric

    ems_sources = list(
        EMSSignalSource.objects.filter(home__user=user)
        .select_related("signal_type", "device")
    )
    ems_pv_ids = {s.device_id for s in ems_sources if s.signal_type.key in ["pv", "solar", "producer", "production"]}
    ems_battery_ids = {s.device_id for s in ems_sources if s.signal_type.key in ["battery", "storage"]}
    ems_grid_ids = {s.device_id for s in ems_sources if s.signal_type.key in ["grid", "grid_import", "grid_feed_in", "meter"]}
    ems_consumer_ids = {s.device_id for s in ems_sources if s.signal_type.key in ["consumer", "load", "consumption"]}

    pv_device_ids = set(ems_pv_ids)
    battery_device_ids = set(ems_battery_ids)
    grid_device_ids = set(ems_grid_ids)
    consumer_devices = []

    def _is_non_power_sensor(d):
        cfg = getattr(d, "config", None)
        if cfg and cfg.metric_definition:
            u = (cfg.metric_definition.unit or "").strip().lower()
            k = (cfg.metric_definition.key or "").strip().lower()
            if u in ["a", "v", "%", "°c", "c", "bar", "hz"] or k in [
                "current", "battery_current", "voltage", "battery_voltage",
                "soc", "battery_soc", "battery_level", "temperature", "frequency"
            ]:
                return True
        d_name = (get_device_name(d) or "").lower()
        d_ident = (d.identifier or "").lower()
        if any(w in d_name or w in d_ident for w in ["_current", "_voltage", "_soc", "_level", "stromstärke", "spannung"]):
            if not any(w in d_name or w in d_ident for w in ["power", "leistung", "wirkleistung", "watt"]):
                return True
        return False

    for d in devices:
        if _is_non_power_sensor(d):
            continue

        if d.id in ems_pv_ids:
            continue
        if d.id in ems_battery_ids:
            continue
        if d.id in ems_grid_ids:
            continue

        cfg = getattr(d, "config", None)
        role_key = (cfg.role.key if cfg and cfg.role else "").lower()
        sig_key = (cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else "").lower()
        is_grid = getattr(cfg, "is_grid_source", False)

        dev_name = (get_device_name(d) or "").lower()
        dev_ident = (d.identifier or "").lower()

        if is_grid or role_key == "grid" or sig_key in ["grid", "grid_import", "grid_feed_in", "meter"] or "grid" in dev_name:
            grid_device_ids.add(d.id)
        elif role_key in ["producer", "pv", "solar", "inverter", "wechselrichter", "balkonkraftwerk"] or sig_key in ["pv", "solar", "producer", "production"] or any(k in dev_name for k in ["solar", "wechselrichter", "inverter", "balkonkraftwerk", "pv-", "bkw", "pv"]) or any(k in dev_ident for k in ["solar", "inverter", "pv"]):
            pv_device_ids.add(d.id)
        elif role_key in ["battery", "storage", "speicher", "batterie"] or sig_key in ["battery", "storage"] or any(k in dev_name for k in ["speicher", "batterie", "battery"]):
            battery_device_ids.add(d.id)
        else:
            consumer_devices.append(d)

    try:
        from producer.models import GeneratorSystem, StorageSystem
        for gs in GeneratorSystem.objects.filter(home__user=user, active=True).select_related("device__config__metric_definition"):
            if gs.device_id and not _is_non_power_sensor(gs.device):
                pv_device_ids.add(gs.device_id)
                grid_device_ids.discard(gs.device_id)
                battery_device_ids.discard(gs.device_id)
                consumer_devices = [d for d in consumer_devices if d.id != gs.device_id]

        for ss in StorageSystem.objects.filter(home__user=user, active=True).select_related(
            "power_device__config__metric_definition", "primary_device__config__metric_definition"
        ):
            b_ids = {ss.power_device_id, ss.primary_device_id, ss.soc_device_id, ss.current_device_id, ss.voltage_device_id} - {None}
            for b_id in b_ids:
                dev_obj = next((d for d in devices if d.id == b_id), None)
                is_hybrid = False
                if dev_obj and hasattr(dev_obj, "config") and dev_obj.config:
                    role_k = getattr(dev_obj.config.role, "key", None)
                    if role_k in ["both", "hybrid"]:
                        is_hybrid = True
                if not is_hybrid:
                    grid_device_ids.discard(b_id)
                    pv_device_ids.discard(b_id)
                    consumer_devices = [d for d in consumer_devices if d.id != b_id]

            if ss.power_device_id and not _is_non_power_sensor(ss.power_device):
                battery_device_ids.add(ss.power_device_id)
            elif ss.primary_device_id and not _is_non_power_sensor(ss.primary_device):
                battery_device_ids.add(ss.primary_device_id)
    except Exception:
        pass

    # 2. Aggregierte Stunden-Daten aus DeviceMetric1h laden (mit Intraday-Fallbacks)
    all_device_ids = [d.id for d in devices]
    metric_rows = list(
        DeviceMetric1h.objects.filter(
            device_id__in=all_device_ids,
            bucket__gte=start_dt,
            bucket__lte=end_dt,
        ).values("device_id", "metric_key", "bucket", "energy_wh", "avg")
    )

    # Intraday-Fallback 1: 15-Minuten Aggregate
    if not metric_rows and all_device_ids:
        mid_rows = list(
            DeviceMetric15m.objects.filter(
                device_id__in=all_device_ids,
                bucket__gte=start_dt,
                bucket__lte=end_dt,
            ).values("device_id", "metric_key", "bucket", "energy_wh", "avg")
        )
        if mid_rows:
            metric_rows = mid_rows
        else:
            # Intraday-Fallback 2: Roh-Telemetrie des heutigen Tages (sekündlich/minütlich wie bei MQTT/OTel)
            raw_metrics = list(
                DeviceMetric.objects.filter(
                    device_id__in=all_device_ids,
                    timestamp__gte=start_dt,
                    timestamp__lte=end_dt,
                ).values("device_id", "metric_key", "timestamp", "value")
                .order_by("timestamp")
            )
            if raw_metrics:
                dev_hour_map = defaultdict(lambda: defaultdict(list))
                for r in raw_metrics:
                    b_t = r["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
                    m_k = r.get("metric_key") or "power"
                    dev_hour_map[(r["device_id"], m_k)][b_t].append(float(r["value"] or 0))

                for (dev_id, m_k), h_map in dev_hour_map.items():
                    for b_t, vals in h_map.items():
                        avg_w = sum(vals) / len(vals)
                        # Trapez-/Durchschnittsintegration: Watt * Stunden = Wh
                        wh = avg_w * (len(vals) * 60 / 3600.0) if len(vals) < 60 else avg_w
                        metric_rows.append({
                            "device_id": dev_id,
                            "metric_key": m_k,
                            "bucket": b_t,
                            "energy_wh": wh,
                            "avg": avg_w,
                        })

    device_energy_sum = defaultdict(float)
    bucket_map = defaultdict(lambda: {"pv": 0.0, "load": 0.0, "battery_charge": 0.0, "battery_discharge": 0.0, "grid_import": 0.0, "grid_export": 0.0})
    battery_charge_map = defaultdict(float)
    battery_discharge_map = defaultdict(float)
    grid_import_kwh_total = 0.0
    grid_export_kwh_total = 0.0
    pv_kwh_total = 0.0
    load_kwh_total = 0.0

    for row in metric_rows:
        dev_id = row["device_id"]
        m_k = (row.get("metric_key") or "").strip().lower()
        wh = float(row["energy_wh"] or 0)
        avg_w = float(row.get("avg") or 0)
        if wh == 0 and avg_w != 0:
            wh = avg_w  # 1h Intervall: Avg(Watt) * 1h = Wh
        kwh = abs(wh) / 1000.0
        device_energy_sum[dev_id] += kwh

        b_time = row["bucket"].astimezone(tz)
        b_key = b_time.strftime(bucket_format)

        # 1. PV Erzeugung
        if m_k in ["power", "pv_power", "pv_power_w", "pv"] or (
            dev_id in pv_device_ids and m_k not in ["load_power", "grid_power", "battery_power"]
        ):
            bucket_map[b_key]["pv"] += kwh
            pv_kwh_total += kwh

        # 2. Netzleistung (Import / Export)
        elif m_k in ["grid_power", "grid_power_w", "grid"] or (
            dev_id in grid_device_ids and m_k not in ["power", "load_power", "battery_power"]
        ):
            if avg_w >= 0:
                bucket_map[b_key]["grid_import"] += kwh
                grid_import_kwh_total += kwh
            else:
                bucket_map[b_key]["grid_export"] += kwh
                grid_export_kwh_total += kwh

        # 3. Speicherleistung (Discharge / Charge)
        elif m_k in ["battery_power", "battery_power_w", "battery"] or (
            dev_id in battery_device_ids and m_k not in ["power", "load_power", "grid_power"]
        ):
            if avg_w < 0:
                bucket_map[b_key]["battery_charge"] += kwh
                battery_charge_map[dev_id] += kwh
            else:
                bucket_map[b_key]["battery_discharge"] += kwh
                battery_discharge_map[dev_id] += kwh

        # 4. Hausverbrauch / Consumer
        elif m_k in ["load_power", "load_power_w", "load", "consumer"]:
            bucket_map[b_key]["load"] += kwh
            load_kwh_total += kwh

        else:
            bucket_map[b_key]["load"] += kwh
            load_kwh_total += kwh

    total_pv_kwh = round(pv_kwh_total, 2)
    battery_devices = [d for d in devices if d.id in battery_device_ids]
    
    total_battery_charge_kwh = round(sum(battery_charge_map.values()), 2)
    total_battery_discharge_kwh = round(sum(battery_discharge_map.values()), 2)

    # Fallback falls Batterie-Metriken ohne Vorzeichen vorlagen:
    if battery_device_ids and total_battery_charge_kwh == 0 and total_battery_discharge_kwh == 0:
        raw_batt_kwh = sum(device_energy_sum[d_id] for d_id in battery_device_ids if d_id not in pv_device_ids)
        total_battery_discharge_kwh = round(raw_batt_kwh, 2)
        for b_id in battery_device_ids:
            if b_id not in pv_device_ids:
                battery_discharge_map[b_id] = device_energy_sum[b_id]

    total_grid_import_kwh = round(grid_import_kwh_total, 2)
    total_grid_export_kwh = round(grid_export_kwh_total, 2)
    total_measured_consumer_kwh = round(load_kwh_total, 2)

    has_devices = len(devices) > 0
    has_data = (total_pv_kwh > 0 or total_measured_consumer_kwh > 0 or total_grid_import_kwh > 0 or total_battery_charge_kwh > 0 or total_battery_discharge_kwh > 0 or len(metric_rows) > 0)

    if not has_data:
        total_pv_kwh = 0.0
        total_house_consumption_kwh = 0.0
        total_battery_discharge_kwh = 0.0
        total_battery_charge_kwh = 0.0
        total_grid_import_kwh = 0.0
        total_grid_export_kwh = 0.0
        direct_consumption_kwh = 0.0
        solar_supplied_kwh = 0.0
        self_consumption_kwh = 0.0
        autarky_rate = 0.0
        self_consumption_rate = 0.0
    else:
        # Falls kein Netzzähler existiert, Überschusseinspeisung rechnerisch ermitteln
        if not grid_device_ids:
            total_grid_export_kwh = round(max(0.0, total_pv_kwh - total_battery_charge_kwh - total_measured_consumer_kwh), 2)
            total_grid_import_kwh = 0.0

        # Physische Bilanz:
        # 1. Direkter PV-Verbrauch im Haus = PV - Einspeisung - Batterieladung
        direct_consumption_kwh = round(max(0.0, total_pv_kwh - total_grid_export_kwh - total_battery_charge_kwh), 2)
        
        # 2. Gesamt-Hausverbrauch = Direkter PV-Verbrauch + Batterie-Entladung + Netzbezug
        total_house_consumption_kwh = round(direct_consumption_kwh + total_battery_discharge_kwh + total_grid_import_kwh, 2)
        if total_house_consumption_kwh < total_measured_consumer_kwh:
            total_house_consumption_kwh = total_measured_consumer_kwh

        # 3. Bucket-by-Bucket Solardeckung berechnen
        sum_solar_supplied = 0.0
        sum_house_consumption = 0.0
        for b_data in bucket_map.values():
            b_pv = b_data.get("pv", 0.0)
            b_bat_chg = b_data.get("battery_charge", 0.0)
            b_bat_dis = b_data.get("battery_discharge", 0.0)
            b_grid_imp = b_data.get("grid_import", 0.0)
            b_grid_exp = b_data.get("grid_export", 0.0)
            b_load = b_data.get("load", 0.0)

            b_solar_avail = max(0.0, b_pv - b_bat_chg - b_grid_exp) if grid_device_ids else max(0.0, b_pv - b_bat_chg)
            b_house_load = max(b_load, b_solar_avail + b_bat_dis + b_grid_imp)
            b_solar_supplied = min(b_house_load, b_solar_avail + b_bat_dis) if b_house_load > 0 else 0.0

            sum_solar_supplied += b_solar_supplied
            sum_house_consumption += b_house_load

        if total_grid_import_kwh == 0 and total_house_consumption_kwh > 0:
            autarky_rate = 100.0
            solar_supplied_kwh = total_house_consumption_kwh
        elif total_house_consumption_kwh > 0:
            autarky_rate = round(max(0.0, min(100.0, (1.0 - (total_grid_import_kwh / total_house_consumption_kwh)) * 100.0)), 1)
            solar_supplied_kwh = round(max(0.0, total_house_consumption_kwh - total_grid_import_kwh), 2)
        else:
            autarky_rate = 0.0
            solar_supplied_kwh = 0.0

        autarky_rate = min(100.0, max(0.0, autarky_rate))


        # 4. Eigenverbrauchsquote (Wie viel % der PV-Erzeugung wurden direkt verbraucht oder im Speicher geladen?):
        self_consumption_kwh = round(direct_consumption_kwh + total_battery_charge_kwh, 2)
        self_consumption_rate = round((self_consumption_kwh / total_pv_kwh * 100.0), 1) if total_pv_kwh > 0 else 0.0
        self_consumption_rate = min(100.0, max(0.0, self_consumption_rate))

    # =========================================================================
    # 2.5 Tarif-, Börsenpreis- und Einspeisevergütungs-Berechnung (Zeitgenau nach Datum)
    # =========================================================================
    current_active_tariff = get_home_tariff(home, end_dt.date()) if home else None
    tariff_type = current_active_tariff.tariff_type if current_active_tariff else "static"
    feed_in_type = current_active_tariff.feed_in_tariff_type if current_active_tariff else HomeTariff.FEED_IN_STATIC

    spot_prices_map = {}
    if tariff_type == HomeTariff.TARIFF_DYNAMIC or feed_in_type == HomeTariff.FEED_IN_DYNAMIC:
        spot_qs = SpotPrice.objects.filter(
            timestamp__gte=start_dt - timedelta(hours=1),
            timestamp__lte=end_dt + timedelta(hours=1),
        ).values("timestamp", "price_eur_per_kwh")
        for sp in spot_qs:
            ts_key = sp["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
            spot_prices_map[ts_key] = float(sp["price_eur_per_kwh"] or 0.10) * 100.0

    # Bezugsstrompreis-Label für aktuellen Tarif
    if current_active_tariff and current_active_tariff.tariff_type == HomeTariff.TARIFF_STATIC and current_active_tariff.static_price_eur_per_kwh:
        base_elec_price = float(current_active_tariff.static_price_eur_per_kwh)
        tariff_label = f"Festpreis ({base_elec_price * 100:.1f} ct/kWh)"
    elif tariff_type == HomeTariff.TARIFF_DYNAMIC:
        base_elec_price = 0.28
        tariff_label = "Dynamisch (EPEX Spot + Abgaben)"
    else:
        base_elec_price = 0.32
        tariff_label = "Standard-Tarif (32,0 ct/kWh)"

    feed_in_price = (
        float(current_active_tariff.feed_in_tariff_eur_per_kwh)
        if (current_active_tariff and current_active_tariff.feed_in_tariff_eur_per_kwh is not None)
        else 0.082
    )

    # Cache für tagesgenaue Tarife
    tariff_cache = {}
    def get_tariff_for_date(d):
        if d not in tariff_cache:
            tariff_cache[d] = get_home_tariff(home, d) if home else None
        return tariff_cache[d]

    # Finanzen & Ersparnis berechnen (Intervall- und tagesgenau)
    if metric_rows:
        calculated_savings = 0.0
        calculated_grid_costs = 0.0
        calculated_feed_in_revenue = 0.0

        for b_time_dt, vals in sorted(
            [
                (row["bucket"].astimezone(tz).replace(minute=0, second=0, microsecond=0), row)
                for row in metric_rows
            ],
            key=lambda x: x[0],
        ):
            b_date = b_time_dt.date()
            t_obj = get_tariff_for_date(b_date)
            t_type = t_obj.tariff_type if t_obj else tariff_type
            f_type = t_obj.feed_in_tariff_type if t_obj else feed_in_type

            spot_ct = spot_prices_map.get(b_time_dt, 10.5)

            # 1. Strombezugspreis für dieses Intervall
            if t_type == HomeTariff.TARIFF_DYNAMIC:
                effective_ct = calculate_effective_price(home, b_time_dt, spot_ct) if home else (spot_ct + 17.59)
                unit_price_eur = effective_ct / 100.0
            elif t_obj and t_obj.static_price_eur_per_kwh is not None:
                unit_price_eur = float(t_obj.static_price_eur_per_kwh)
            else:
                unit_price_eur = base_elec_price

            # 2. Einspeisepreis für dieses Intervall
            if f_type == HomeTariff.FEED_IN_NONE:
                feed_in_unit_eur = 0.0
            elif f_type == HomeTariff.FEED_IN_DYNAMIC:
                feed_in_unit_eur = max(0.0, spot_ct / 100.0)
            else:
                feed_in_unit_eur = float(t_obj.feed_in_tariff_eur_per_kwh) if (t_obj and t_obj.feed_in_tariff_eur_per_kwh is not None) else 0.082

            dev_id = vals["device_id"]
            wh = float(vals["energy_wh"] or 0)
            kwh = wh / 1000.0

            if dev_id in pv_device_ids:
                calculated_savings += kwh * 0.7 * unit_price_eur
            elif dev_id in grid_device_ids:
                avg_val = float(vals.get("avg", 0))
                if avg_val > 0:
                    calculated_grid_costs += kwh * unit_price_eur
                elif avg_val < 0:
                    calculated_feed_in_revenue += kwh * feed_in_unit_eur

        savings_eur = round(max(calculated_savings, solar_supplied_kwh * 0.20), 2)
        grid_costs_eur = round(max(calculated_grid_costs, total_grid_import_kwh * 0.20), 2)
        feed_in_revenue_eur = round(calculated_feed_in_revenue if calculated_feed_in_revenue > 0 else (total_grid_export_kwh * (float(current_active_tariff.feed_in_tariff_eur_per_kwh) if current_active_tariff and current_active_tariff.feed_in_tariff_eur_per_kwh else 0.082) if feed_in_type == HomeTariff.FEED_IN_STATIC else 0.0), 2)
        elec_price = round(savings_eur / solar_supplied_kwh, 4) if solar_supplied_kwh > 0 else base_elec_price
    else:
        elec_price = base_elec_price
        savings_eur = round(solar_supplied_kwh * elec_price, 2)
        grid_costs_eur = round(total_grid_import_kwh * elec_price, 2)
        feed_in_rate = float(current_active_tariff.feed_in_tariff_eur_per_kwh) if (current_active_tariff and current_active_tariff.feed_in_tariff_eur_per_kwh is not None) else 0.082
        feed_in_revenue_eur = round(total_grid_export_kwh * feed_in_rate, 2) if feed_in_type == HomeTariff.FEED_IN_STATIC else 0.0

    net_benefit_eur = round(savings_eur + feed_in_revenue_eur - grid_costs_eur, 2)
    co2_saved_kg = round(solar_supplied_kwh * 0.40, 1)

    # 3. Sub-Metering & Virtuelle Zähler generieren
    submeters = []
    color_palette = ["#6366f1", "#f59e0b", "#10b981", "#ec4899", "#8b5cf6", "#06b6d4", "#f97316"]
    color_idx = 0
    running_measured_kwh = 0.0

    if has_data and (total_house_consumption_kwh > 0 or total_battery_charge_kwh > 0):
        # A) Reale gemessene Haushalts-Verbraucher (Wallbox, WP, etc.)
        for dev in consumer_devices:
            dev_kwh = round(device_energy_sum[dev.id], 2)
            running_measured_kwh += dev_kwh
            share_pct = round((dev_kwh / total_house_consumption_kwh * 100.0), 1) if total_house_consumption_kwh > 0 else 0.0
            dev_name = get_device_name(dev)
            icon, category = get_consumer_icon_and_category(dev_name, "consumer")

            submeters.append({
                "id": dev.id,
                "name": dev_name,
                "icon": icon,
                "category": category,
                "consumption_kwh": dev_kwh,
                "share_pct": share_pct,
                "solar_share_pct": autarky_rate,
                "cost_eur": round(dev_kwh * ((100 - autarky_rate) / 100.0) * elec_price, 2),
                "savings_eur": round(dev_kwh * (autarky_rate / 100.0) * elec_price, 2),
                "color": color_palette[color_idx % len(color_palette)],
                "is_residual": False,
                "is_battery": False,
            })
            color_idx += 1

        # B) Batteriespeicher-Ladung als virtueller Zähler / Energie-Puffer
        for b_dev in battery_devices:
            b_charge_kwh = round(battery_charge_map.get(b_dev.id, 0.0), 2)
            if b_charge_kwh > 0:
                b_name = get_device_name(b_dev)
                total_energy_allocated = total_house_consumption_kwh + total_battery_charge_kwh
                b_share = round((b_charge_kwh / total_energy_allocated * 100.0), 1) if total_energy_allocated > 0 else 0.0
                submeters.append({
                    "id": b_dev.id,
                    "name": f"{b_name} (Akkuladung)",
                    "icon": "🔋",
                    "category": "battery",
                    "consumption_kwh": b_charge_kwh,
                    "share_pct": b_share,
                    "solar_share_pct": 100.0,
                    "cost_eur": 0.0,
                    "savings_eur": round(b_charge_kwh * elec_price, 2),
                    "color": "#8b5cf6",
                    "is_residual": False,
                    "is_battery": True,
                })

        # C) Automatischer Residual-Zähler (Restlicher Hausverbrauch / Grundlast)
        residual_kwh = round(max(0.0, total_house_consumption_kwh - running_measured_kwh), 2)
        if residual_kwh > 0 or not submeters:
            residual_share = round((residual_kwh / total_house_consumption_kwh * 100.0), 1) if total_house_consumption_kwh > 0 else 0.0
            submeters.append({
                "id": "residual",
                "name": "Restlicher Hausverbrauch (Grundlast)",
                "icon": "💡",
                "category": "residual",
                "consumption_kwh": residual_kwh,
                "share_pct": residual_share,
                "solar_share_pct": autarky_rate,
                "cost_eur": round(residual_kwh * ((100 - autarky_rate) / 100.0) * elec_price, 2),
                "savings_eur": round(residual_kwh * (autarky_rate / 100.0) * elec_price, 2),
                "color": "#94a3b8",
                "is_residual": True,
                "is_battery": False,
            })

    # Donut Chart Data
    breakdown_data = [
        {"name": s["name"], "value": s["consumption_kwh"], "color": s["color"]}
        for s in submeters
    ]

    # Time series for stacked bars
    timeseries_data = []
    if bucket_map:
        for b_label, vals in sorted(bucket_map.items()):
            timeseries_data.append({
                "time": b_label,
                "pv": round(vals["pv"], 2),
                "load": round(vals["load"], 2),
                "battery_discharge": round(vals["battery_discharge"], 2),
                "grid_import": round(vals["grid_import"], 2),
                "grid_export": round(vals["grid_export"], 2),
            })

    # Insights
    insights = []
    if not has_data:
        insights.append("Noch keine Messdaten für diesen Zeitraum vorhanden. Verbinde deine Geräte unter 'Geräte', um deine Energieflüsse live zu erfassen.")
    else:
        if autarky_rate >= 75.0:
            insights.append(f"Exzellente Autarkie: {autarky_rate} % deines Strombedarfs stammten im Zeitraum aus eigener Solarenergie.")
        elif autarky_rate >= 50.0:
            insights.append(f"Gute Eigenversorgung: {autarky_rate} % solarer Deckungsgrad im gewählten Zeitraum.")
        else:
            insights.append(f"Hoher Netzbezug: Nur {autarky_rate} % deines Strombedarfs wurden durch PV/Speicher gedeckt.")

        top_consumer = max(submeters, key=lambda s: s["consumption_kwh"]) if submeters else None
        if top_consumer and not top_consumer.get("is_residual") and top_consumer["consumption_kwh"] > 0:
            insights.append(f"Größter Verbraucher: {top_consumer['name']} mit {top_consumer['share_pct']} % des Gesamtstroms ({top_consumer['solar_share_pct']}% Solaranteil).")

        if net_benefit_eur > 0:
            insights.append(f"Finanzieller Vorteil: Durch Eigenverbrauch und Einspeisung wurden netto {net_benefit_eur:.2f} € erzielt.")

    # Zusätzliche Metriken & Benchmarks
    days_count = 1 if period == "today" else (7 if period == "7d" else (30 if period == "30d" else 365))
    daily_avg_gen = round(total_pv_kwh / days_count, 1)
    daily_avg_con = round(total_house_consumption_kwh / days_count, 1)

    pv_peaks = [row.get("avg", 0) for row in metric_rows if row["device_id"] in pv_device_ids]
    peak_pv_kw = round(max(pv_peaks) / 1000.0, 1) if pv_peaks else 0.0

    load_peaks = [row.get("avg", 0) for row in metric_rows if row["device_id"] not in pv_device_ids and row["device_id"] not in grid_device_ids]
    peak_load_kw = round(max(load_peaks) / 1000.0, 1) if load_peaks else 0.0

    trees_equivalent = round(co2_saved_kg / 12.5, 1)
    ev_km_equivalent = round(solar_supplied_kwh * 6.0, 0)

    return {
        "period": period,
        "period_label": period_label,
        "has_devices": has_devices,
        "has_data": has_data,
        "kpis": {
            "pv_generation_kwh": total_pv_kwh,
            "house_consumption_kwh": total_house_consumption_kwh,
            "battery_charge_kwh": total_battery_charge_kwh,
            "battery_discharge_kwh": total_battery_discharge_kwh,
            "grid_import_kwh": total_grid_import_kwh,
            "grid_export_kwh": total_grid_export_kwh,
            "direct_consumption_kwh": direct_consumption_kwh,
            "solar_supplied_kwh": solar_supplied_kwh,
            "autarky_rate": autarky_rate,
            "autarky_pct": autarky_rate,
            "self_consumption_rate": self_consumption_rate,
            "self_consumption_pct": self_consumption_rate,
            "savings_eur": savings_eur,
            "feed_in_revenue_eur": feed_in_revenue_eur,
            "grid_costs_eur": grid_costs_eur,
            "net_benefit_eur": net_benefit_eur,
            "co2_saved_kg": co2_saved_kg,
            "peak_pv_kw": peak_pv_kw,
            "peak_load_kw": peak_load_kw,
            "daily_avg_generation_kwh": daily_avg_gen,
            "daily_avg_consumption_kwh": daily_avg_con,
            "trees_equivalent": trees_equivalent,
            "ev_km_equivalent": ev_km_equivalent,
            "tariff_elec_eur_kwh": elec_price,
            "tariff_feedin_eur_kwh": feed_in_price,
            "tariff_type": tariff_type,
            "tariff_label": tariff_label,
            "feed_in_tariff_type": feed_in_type,
        },
        "submeters": submeters,
        "charts": {
            "breakdown": breakdown_data,
            "timeseries": timeseries_data,
        },
        "insights": insights,
    }
