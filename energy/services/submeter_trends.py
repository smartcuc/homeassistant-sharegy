####################################
# energy/services/submeter_trends.py
####################################

from datetime import timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone
from collections import defaultdict

from devices.models import Device, DeviceMetric1h
from market.models_tariff import HomeTariff
from market.services_tariff import get_home_tariff, calculate_effective_price
from market.models import SpotPrice
from energy.services.balance import get_device_name, get_consumer_icon_and_category, get_period_range


def get_submeter_trends(user, period: str = "30d", meter_id: str = None) -> dict:
    """
    Berechnet historische Trends, Verbrauchsverläufe und solare Deckungsanalysen
    für alle virtuellen Zähler (Submeter) und den Residual-Restverbraucher.
    """
    home = user.homes.first() if hasattr(user, "homes") else None
    tz_name = home.timezone if home and home.timezone else "Europe/Berlin"
    tz = ZoneInfo(tz_name)

    start_dt, end_dt, period_label, bucket_format = get_period_range(period, tz)

    # 1. Geräte des Haushalts laden
    devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        ).select_related("config__role", "config__energy_signal_type")
    )

    # 1. EMS Signal Sources laden (höchste Priorität für die Zuordnung)
    from energy.ems.models import EMSSignalSource
    from devices.models import DeviceMetric15m, DeviceMetric

    ems_sources = list(
        EMSSignalSource.objects.filter(home__user=user)
        .select_related("signal_type", "device")
    )
    ems_pv_ids = {s.device_id for s in ems_sources if s.signal_type.key in ["pv", "solar", "producer", "production"]}
    ems_battery_ids = {s.device_id for s in ems_sources if s.signal_type.key in ["battery", "storage"]}
    ems_grid_ids = {s.device_id for s in ems_sources if s.signal_type.key in ["grid", "grid_import", "grid_feed_in", "meter"]}

    pv_device_ids = set(ems_pv_ids)
    battery_device_ids = set(ems_battery_ids)
    grid_device_ids = set(ems_grid_ids)
    consumer_devices = []

    for d in devices:
        if d.id in ems_pv_ids or d.id in ems_battery_ids or d.id in ems_grid_ids:
            continue

        cfg = getattr(d, "config", None)
        role_key = (cfg.role.key if cfg and cfg.role else "").lower()
        sig_key = (cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else "").lower()
        is_grid = getattr(cfg, "is_grid_source", False)

        dev_name = (get_device_name(d) or "").lower()
        dev_ident = (d.identifier or "").lower()

        # Nicht-Wirkleistungs-Sensoren (A, V, %, °C) aus Energie-Bilanzsummen ausschließen
        mdef = cfg.metric_definition if cfg else None
        if mdef:
            u = (mdef.unit or "").strip().lower()
            k = (mdef.key or "").strip().lower()
            if u in ["a", "v", "%", "°c", "c", "bar", "hz"] or k in [
                "current", "battery_current", "voltage", "battery_voltage",
                "soc", "battery_soc", "battery_level", "temperature", "frequency"
            ]:
                continue
        if any(w in dev_name or w in dev_ident for w in ["_current", "_voltage", "_soc", "_level", "stromstärke", "spannung"]):
            if not any(w in dev_name or w in dev_ident for w in ["power", "leistung", "wirkleistung", "watt"]):
                continue

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
        for gs in GeneratorSystem.objects.filter(home__user=user, active=True).select_related("device"):
            if gs.device_id:
                pv_device_ids.add(gs.device_id)

        for ss in StorageSystem.objects.filter(home__user=user, active=True).select_related("power_device", "primary_device"):
            if ss.power_device_id:
                battery_device_ids.add(ss.power_device_id)
            elif ss.primary_device_id:
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
        ).values("device_id", "bucket", "energy_wh", "avg")
    )

    if not metric_rows and all_device_ids:
        mid_rows = list(
            DeviceMetric15m.objects.filter(
                device_id__in=all_device_ids,
                bucket__gte=start_dt,
                bucket__lte=end_dt,
            ).values("device_id", "bucket", "energy_wh", "avg")
        )
        if mid_rows:
            metric_rows = mid_rows
        else:
            raw_metrics = list(
                DeviceMetric.objects.filter(
                    device_id__in=all_device_ids,
                    timestamp__gte=start_dt,
                    timestamp__lte=end_dt,
                ).values("device_id", "timestamp", "value")
                .order_by("timestamp")
            )
            if raw_metrics:
                dev_hour_map = defaultdict(lambda: defaultdict(list))
                for r in raw_metrics:
                    b_t = r["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
                    dev_hour_map[r["device_id"]][b_t].append(float(r["value"] or 0))

                for dev_id, h_map in dev_hour_map.items():
                    for b_t, vals in h_map.items():
                        avg_w = sum(vals) / len(vals)
                        wh = avg_w * (len(vals) * 5 / 3600.0) if len(vals) < 720 else avg_w
                        metric_rows.append({
                            "device_id": dev_id,
                            "bucket": b_t,
                            "energy_wh": wh,
                            "avg": avg_w,
                        })

    # 3. Aktiven Tarif & Börsenpreise laden
    current_active_tariff = get_home_tariff(home, end_dt.date()) if home else None
    tariff_type = current_active_tariff.tariff_type if current_active_tariff else "static"
    base_elec_price = (
        float(current_active_tariff.static_price_eur_per_kwh)
        if current_active_tariff and current_active_tariff.static_price_eur_per_kwh
        else 0.32
    )

    tariff_label = f"Festpreis ({base_elec_price * 100:.1f} ct/kWh)" if tariff_type == "static" else "Dynamisch (EPEX Spot)"

    spot_prices_map = {}
    if tariff_type == HomeTariff.TARIFF_DYNAMIC:
        spot_qs = SpotPrice.objects.filter(
            timestamp__gte=start_dt - timedelta(hours=1),
            timestamp__lte=end_dt + timedelta(hours=1),
        ).values("timestamp", "price_eur_per_kwh")
        for sp in spot_qs:
            ts_key = sp["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
            spot_prices_map[ts_key] = float(sp["price_eur_per_kwh"] or 0.10) * 100.0

    # 4. Zeitreihen-Struktur aufbauen
    # Key: bucket_str (z. B. "25.08." oder "14:00") -> Daten
    bucket_order = []
    bucket_data = defaultdict(lambda: {
        "pv_kwh": 0.0,
        "battery_charge_kwh": 0.0,
        "battery_discharge_kwh": 0.0,
        "grid_import_kwh": 0.0,
        "grid_export_kwh": 0.0,
        "total_load_kwh": 0.0,
        "consumers": defaultdict(float),  # meter_id -> kwh
        "tariff_price_eur": base_elec_price,
    })

    # Vorbefüllung aller Buckets im Zeitraum für lückenlose Achsen
    curr_time = start_dt
    step = timedelta(hours=1) if period == "today" else timedelta(days=1)
    while curr_time <= end_dt:
        b_key = curr_time.strftime(bucket_format)
        if b_key not in bucket_order:
            bucket_order.append(b_key)
        curr_time += step

    price_cache = {}

    def get_price_for_time(b_time):
        h_key = b_time.replace(minute=0, second=0, microsecond=0)
        if h_key in price_cache:
            return price_cache[h_key]
        if tariff_type == HomeTariff.TARIFF_DYNAMIC:
            spot_ct = spot_prices_map.get(h_key, 10.5)
            effective_ct = calculate_effective_price(home, b_time, spot_ct) if home else (spot_ct + 17.59)
            res = effective_ct / 100.0
        else:
            res = base_elec_price
        price_cache[h_key] = res
        return res

    for row in metric_rows:
        dev_id = row["device_id"]
        wh = float(row["energy_wh"] or 0)
        avg_w = float(row.get("avg") or 0)
        if wh == 0 and avg_w > 0:
            wh = avg_w  # 1h Intervall: Avg(Watt) * 1h = Wh
        kwh = wh / 1000.0
        b_time = row["bucket"].astimezone(tz)
        b_key = b_time.strftime(bucket_format)

        if b_key not in bucket_order:
            bucket_order.append(b_key)

        entry = bucket_data[b_key]
        entry["tariff_price_eur"] = get_price_for_time(b_time)

        if dev_id in pv_device_ids:
            entry["pv_kwh"] += kwh
        elif dev_id in battery_device_ids:
            avg_w = float(row.get("avg") or 0)
            if avg_w >= 0:
                entry["battery_charge_kwh"] += kwh
                entry["consumers"][str(dev_id)] += kwh
            else:
                entry["battery_discharge_kwh"] += kwh
        elif dev_id in grid_device_ids:
            avg_w = float(row.get("avg") or 0)
            if avg_w > 0:
                entry["grid_import_kwh"] += kwh
            else:
                entry["grid_export_kwh"] += kwh
        elif any(c.id == dev_id for c in consumer_devices):
            entry["consumers"][str(dev_id)] += kwh
            entry["total_load_kwh"] += kwh
        else:
            entry["total_load_kwh"] += kwh

    # Farbpalette
    color_palette = ["#6366f1", "#f59e0b", "#10b981", "#ec4899", "#8b5cf6", "#06b6d4", "#f97316"]

    # 5. Definition aller virtuellen Zähler (Metadaten)
    battery_devices = [d for d in devices if d.id in battery_device_ids]
    meters_meta = []
    if consumer_devices or battery_devices:
        for idx, dev in enumerate(consumer_devices):
            dev_name = get_device_name(dev)
            icon, category = get_consumer_icon_and_category(dev_name, "consumer")
            meters_meta.append({
                "id": str(dev.id),
                "name": dev_name,
                "icon": icon,
                "category": category,
                "color": color_palette[idx % len(color_palette)],
                "is_residual": False,
                "is_battery": False,
            })

        for b_idx, b_dev in enumerate(battery_devices):
            dev_name = get_device_name(b_dev)
            meters_meta.append({
                "id": str(b_dev.id),
                "name": f"{dev_name} (Akkuladung)",
                "icon": "🔋",
                "category": "battery",
                "color": "#8b5cf6",
                "is_residual": False,
                "is_battery": True,
            })

        # Residual-Zähler ergänzen
        meters_meta.append({
            "id": "residual",
            "name": "Restlicher Hausverbrauch (Grundlast)",
            "icon": "💡",
            "category": "residual",
            "color": "#94a3b8",
            "is_residual": True,
            "is_battery": False,
        })

    # 6. Zeitreihen auswerten & per-Meter Statistiken aufbauen
    timeseries = []
    meter_totals = defaultdict(lambda: {
        "total_kwh": 0.0,
        "solar_kwh": 0.0,
        "grid_kwh": 0.0,
        "cost_eur": 0.0,
        "savings_eur": 0.0,
        "peak_kwh": 0.0,
        "peak_date": "",
    })

    has_real_metrics = len(metric_rows) > 0

    if meters_meta and has_real_metrics:
        for b_idx, b_key in enumerate(bucket_order):
            b_entry = bucket_data[b_key]
            tariff_price = b_entry["tariff_price_eur"]

            ts_point = {
                "date": b_key,
                "meters": {},
                "total_load_kwh": 0.0,
                "total_solar_covered_kwh": 0.0,
                "total_grid_kwh": 0.0,
            }

            pv_kwh = b_entry["pv_kwh"]
            batt_discharge = b_entry["battery_discharge_kwh"]
            solar_available = pv_kwh + batt_discharge
            tot_load = b_entry["total_load_kwh"]

            # Solare Deckungsquote in diesem Bucket (0.0 bis 1.0)
            solar_coverage_ratio = min(1.0, solar_available / max(tot_load, 0.001)) if tot_load > 0 else 0.0

            measured_sub_sum = 0.0

            for m in meters_meta:
                m_id = m["id"]
                if not m["is_residual"]:
                    m_kwh = b_entry["consumers"][m_id]
                    if not m.get("is_battery"):
                        measured_sub_sum += m_kwh
                else:
                    m_kwh = max(0.0, tot_load - measured_sub_sum)

                if m.get("is_battery"):
                    m_solar = m_kwh
                    m_grid = 0.0
                else:
                    m_solar = round(m_kwh * solar_coverage_ratio, 3)
                    m_grid = round(m_kwh * (1.0 - solar_coverage_ratio), 3)

                m_cost = round(m_grid * tariff_price, 3)
                m_savings = round(m_solar * tariff_price, 3)

                ts_point["meters"][m_id] = {
                    "kwh": round(m_kwh, 2),
                    "solar_kwh": round(m_solar, 2),
                    "grid_kwh": round(m_grid, 2),
                    "cost_eur": round(m_cost, 2),
                    "savings_eur": round(m_savings, 2),
                }

                # Totals aktualisieren
                stats = meter_totals[m_id]
                stats["total_kwh"] += m_kwh
                stats["solar_kwh"] += m_solar
                stats["grid_kwh"] += m_grid
                stats["cost_eur"] += m_cost
                stats["savings_eur"] += m_savings
                if m_kwh > stats["peak_kwh"]:
                    stats["peak_kwh"] = m_kwh
                    stats["peak_date"] = b_key

                ts_point["total_load_kwh"] += m_kwh
                ts_point["total_solar_covered_kwh"] += m_solar
                ts_point["total_grid_kwh"] += m_grid

            ts_point["total_load_kwh"] = round(ts_point["total_load_kwh"], 2)
            ts_point["total_solar_covered_kwh"] = round(ts_point["total_solar_covered_kwh"], 2)
            ts_point["total_grid_kwh"] = round(ts_point["total_grid_kwh"], 2)
            timeseries.append(ts_point)

    # 7. Aggregierte Übersichtskarten für jeden Zähler berechnen
    days_count = max(1, len(timeseries))
    total_all_meters_kwh = sum(meter_totals[m["id"]]["total_kwh"] for m in meters_meta) or 1.0

    meters_summary = []
    for m in meters_meta:
        m_id = m["id"]
        st = meter_totals[m_id]
        tot_k = round(st["total_kwh"], 1)
        sol_k = round(st["solar_kwh"], 1)
        grid_k = round(st["grid_kwh"], 1)
        cost_e = round(st["cost_eur"], 2)
        save_e = round(st["savings_eur"], 2)

        solar_pct = round((sol_k / tot_k * 100.0), 1) if tot_k > 0 else 0.0
        share_pct = round((tot_k / total_all_meters_kwh * 100.0), 1)
        avg_daily = round(tot_k / days_count, 2)

        meters_summary.append({
            "id": m_id,
            "name": m["name"],
            "icon": m["icon"],
            "category": m["category"],
            "color": m["color"],
            "is_residual": m["is_residual"],
            "total_kwh": tot_k,
            "solar_kwh": sol_k,
            "grid_kwh": grid_k,
            "solar_share_pct": solar_pct,
            "share_pct": share_pct,
            "cost_eur": cost_e,
            "savings_eur": save_e,
            "avg_daily_kwh": avg_daily,
            "peak_day_kwh": round(st["peak_kwh"], 2),
            "peak_day_date": st["peak_date"],
        })

    # 8. Detail-Zeitreihe für den ausgewählten Zähler (Default: Erster Zähler)
    selected_id = meter_id or (meters_meta[0]["id"] if meters_meta else "residual")
    selected_meta = next((m for m in meters_summary if m["id"] == selected_id), meters_summary[0] if meters_summary else None)

    selected_detail_timeseries = []
    for pt in timeseries:
        m_vals = pt["meters"].get(selected_id, {"kwh": 0, "solar_kwh": 0, "grid_kwh": 0, "cost_eur": 0, "savings_eur": 0})
        selected_detail_timeseries.append({
            "date": pt["date"],
            "kwh": m_vals["kwh"],
            "solar_kwh": m_vals["solar_kwh"],
            "grid_kwh": m_vals["grid_kwh"],
            "cost_eur": m_vals["cost_eur"],
            "savings_eur": m_vals["savings_eur"],
        })

    return {
        "period": period,
        "period_label": period_label,
        "days_count": days_count,
        "tariff_label": tariff_label,
        "meters": meters_summary,
        "timeseries": timeseries,
        "selected_meter": selected_meta,
        "selected_timeseries": selected_detail_timeseries,
    }

