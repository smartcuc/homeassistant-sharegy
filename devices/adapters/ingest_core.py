"""
devices/adapters/ingest_core.py

Zentraler Standard-Ingest Core für Wechselrichter und Batteriespeicher.
Verarbeitet ausschließlich typisierte CanonicalTelemetry-Objekte.
Vollkommen frei von herstellerspezifischen Sonderregeln!
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.core.cache import cache

from devices.models import Device, DeviceMetric, DeviceLatestMetric, DeviceConfig, DeviceRole, MetricDefinition
from devices.adapters.contracts import CanonicalTelemetry
from devices.services.ingest import broadcast_live_update

logger = logging.getLogger(__name__)


def process_canonical_telemetry(
    device: Device,
    telemetry: CanonicalTelemetry,
    source: str = "cloud_poll",
    device_name: Optional[str] = None,
    battery_capacity_kwh: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Standard-Pipeline zur Persistierung, Cache-Aktualisierung und WebSocket-Verteilung
    von normalisierten Wechselrichter-Daten.
    """
    # 1. Validieren & Plausibilisieren
    telemetry.validate()
    metrics = telemetry.to_metrics_dict()
    now = telemetry.timestamp or timezone.now()

    # 2. PV Leistung
    if telemetry.pv_power_w is not None:
        val = float(telemetry.pv_power_w)
        DeviceMetric.objects.create(
            device=device,
            metric_key="power",
            unit="W",
            value=val,
            timestamp=now,
        )
        DeviceMetric.objects.create(
            device=device,
            metric_key="pv_power",
            unit="W",
            value=val,
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="pv_power",
            defaults={"value": val, "timestamp": now},
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="power",
            defaults={"value": val, "timestamp": now},
        )
        try:
            cache.set(f"device:{device.id}:latest_power", val, timeout=3600)
            cache.set(f"device:{device.id}:pv_power", val, timeout=3600)
        except Exception as e:
            logger.warning("Cache write failed for pv_power: %s", e)

        # GeneratorSystem Verknüpfung
        if device.home:
            try:
                from producer.models import GeneratorSystem
                gen = GeneratorSystem.objects.filter(home=device.home).first()
                if not gen:
                    GeneratorSystem.objects.create(
                        home=device.home,
                        name=device_name or f"{device.identifier} PV-Anlage",
                        device=device,
                        peak_power_kw=10.0,
                        active=True,
                    )
                elif not gen.device:
                    gen.device = device
                    gen.active = True
                    gen.save(update_fields=["device", "active"])
            except Exception as gen_err:
                logger.warning("Could not auto-link GeneratorSystem: %s", gen_err)

    # 3. Tagesertrag (Daily Yield)
    if telemetry.daily_yield_kwh is not None:
        yield_val = float(telemetry.daily_yield_kwh)
        DeviceMetric.objects.create(
            device=device,
            metric_key="daily_yield",
            unit="kWh",
            value=yield_val,
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="daily_yield",
            defaults={"value": yield_val, "timestamp": now},
        )
        try:
            cache.set(f"device:{device.id}:daily_yield", yield_val, timeout=3600)
        except Exception as e:
            logger.warning("Cache write failed for daily_yield: %s", e)

    # 4. Batterie SoC & Leistung
    has_battery = False
    if telemetry.battery_soc is not None:
        has_battery = True
        soc_val = float(telemetry.battery_soc)
        DeviceMetric.objects.create(
            device=device,
            metric_key="battery_soc",
            unit="%",
            value=soc_val,
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="battery_soc",
            defaults={"value": soc_val, "timestamp": now},
        )
        try:
            cache.set(f"device:{device.id}:battery_soc", soc_val, timeout=3600)
            cache.set(f"device:{device.id}:latest_soc", soc_val, timeout=3600)
        except Exception as e:
            logger.warning("Cache write failed for battery_soc: %s", e)

    if telemetry.battery_power_w is not None:
        has_battery = True
        bat_pwr = float(telemetry.battery_power_w)
        DeviceMetric.objects.create(
            device=device,
            metric_key="battery_power",
            unit="W",
            value=bat_pwr,
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="battery_power",
            defaults={"value": bat_pwr, "timestamp": now},
        )
        try:
            cache.set(f"device:{device.id}:battery_power", bat_pwr, timeout=3600)
        except Exception as e:
            logger.warning("Cache write failed for battery_power: %s", e)

    # 5. Hausverbrauch & Netzleistung
    if telemetry.load_power_w is not None:
        load_val = float(telemetry.load_power_w)
        DeviceMetric.objects.create(
            device=device,
            metric_key="load_power",
            unit="W",
            value=load_val,
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="load_power",
            defaults={"value": load_val, "timestamp": now},
        )
        try:
            cache.set(f"device:{device.id}:load_power", load_val, timeout=3600)
        except Exception as e:
            logger.warning("Cache write failed for load_power: %s", e)

    if telemetry.grid_power_w is not None:
        grid_val = float(telemetry.grid_power_w)
        DeviceMetric.objects.create(
            device=device,
            metric_key="grid_power",
            unit="W",
            value=grid_val,
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="grid_power",
            defaults={"value": grid_val, "timestamp": now},
        )
        try:
            cache.set(f"device:{device.id}:grid_power", grid_val, timeout=3600)
        except Exception as e:
            logger.warning("Cache write failed for grid_power: %s", e)

    # 6. DeviceConfig Rollen- und Namenszuordnung
    try:
        role_key = "both" if has_battery else "producer"
        target_role = DeviceRole.objects.filter(key=role_key).first() or DeviceRole.objects.filter(key="producer").first()
        p_metric = MetricDefinition.objects.filter(key="power").first()
        dev_cfg, _ = DeviceConfig.objects.get_or_create(
            device=device,
            defaults={
                "home": device.home,
                "name": device_name or f"{device.identifier} Hybrid-Anlage",
                "role": target_role,
                "metric_definition": p_metric,
            }
        )
        if not dev_cfg.role:
            dev_cfg.role = target_role
            dev_cfg.save(update_fields=["role"])
    except Exception as cfg_err:
        logger.warning("Could not set DeviceConfig: %s", cfg_err)

    # 6. StorageSystem Verknüpfung (falls Speicher vorhanden)
    if has_battery and device.home:
        try:
            from producer.models import StorageSystem
            desired_cap = float(battery_capacity_kwh or 22.0)
            storages = list(StorageSystem.objects.filter(home=device.home))
            if not storages:
                StorageSystem.objects.create(
                    home=device.home,
                    name=f"{device_name or 'Hybrid'} Speicher",
                    primary_device=device,
                    soc_device=device,
                    power_device=device,
                    soc_metric_key="battery_soc",
                    power_metric_key="battery_power",
                    capacity_kwh=desired_cap,
                    max_charge_power_kw=10.0,
                    max_discharge_power_kw=10.0,
                    is_auto_detected=True,
                )
            else:
                for st in storages:
                    if not st.soc_device or st.soc_device == device or "hybrid" in st.name.lower() or "sungrow" in st.name.lower():
                        st.primary_device = device
                        st.soc_device = device
                        st.power_device = device
                        st.soc_metric_key = "battery_soc"
                        st.power_metric_key = "battery_power"
                        if float(st.capacity_kwh) in (9.6, 10.0):
                            st.capacity_kwh = desired_cap
                        st.save()
        except Exception as st_err:
            logger.warning("Could not auto-link StorageSystem: %s", st_err)

    # 7. Device Status aktualisieren
    device.last_seen = now
    device.active = True
    device.save(update_fields=["last_seen", "active"])

    # 8. Live WebSocket Broadcast
    try:
        if telemetry.pv_power_w is not None:
            broadcast_live_update(device, "power", float(telemetry.pv_power_w), "W", now)
        if telemetry.battery_soc is not None:
            broadcast_live_update(device, "battery_soc", float(telemetry.battery_soc), "%", now)
    except Exception:
        pass

    return metrics
