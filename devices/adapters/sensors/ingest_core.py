"""
devices/adapters/sensors/ingest_core.py

Zentraler Standard-Ingest Core für Sensoren, Zwischenstecker und SmartMeter.
Verarbeitet typisierte CanonicalSensorReading-Objekte vollkommen entkoppelt
vom Übertragungsprotokoll (WebSocket, MQTT, REST).
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.core.cache import cache

from devices.models import Device, DeviceMetric, DeviceLatestMetric
from devices.adapters.sensors.contracts import CanonicalSensorReading
from devices.services.ingest import broadcast_live_update

logger = logging.getLogger(__name__)


def process_canonical_sensor_reading(
    device: Device,
    reading: CanonicalSensorReading,
    source: str = "websocket",
) -> Dict[str, Any]:
    """
    Persistiert standardisierte Sensordaten in TimescaleDB (DeviceMetric),
    Redis (DeviceLatestMetric / Caches) und sendet WebSocket Live-Updates.
    """
    reading.validate()
    metrics = reading.to_metrics_dict()
    now = reading.timestamp or timezone.now()

    # 1. Leistung (W)
    if reading.power_w is not None:
        p_val = float(reading.power_w)
        DeviceMetric.objects.create(
            device=device,
            metric_key="power",
            unit="W",
            value=p_val,
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="power",
            defaults={"value": p_val, "timestamp": now},
        )
        try:
            cache.set(f"device:{device.id}:latest_power", p_val, timeout=3600)
            cache.set(f"device:{device.id}:power", p_val, timeout=3600)
        except Exception as e:
            logger.warning("Cache write failed for sensor power: %s", e)

        try:
            broadcast_live_update(device, "power", p_val, "W", now)
        except Exception:
            pass

    # 2. Energie (kWh)
    if reading.energy_import_kwh is not None:
        e_val = float(reading.energy_import_kwh)
        DeviceMetric.objects.create(
            device=device,
            metric_key="energy",
            unit="kWh",
            value=e_val,
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="energy",
            defaults={"value": e_val, "timestamp": now},
        )
        try:
            cache.set(f"device:{device.id}:latest_energy", e_val, timeout=3600)
        except Exception as e:
            logger.warning("Cache write failed for sensor energy: %s", e)

    # 3. Spannung & Strom
    if reading.voltage_l1_v is not None:
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="voltage",
            defaults={"value": float(reading.voltage_l1_v), "timestamp": now},
        )
    if reading.current_l1_a is not None:
        total_curr = (reading.current_l1_a or 0.0) + (reading.current_l2_a or 0.0) + (reading.current_l3_a or 0.0)
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="current",
            defaults={"value": round(total_curr, 3), "timestamp": now},
        )

    # 4. Frequenz & Temperatur & SoC
    if reading.frequency_hz is not None:
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="frequency",
            defaults={"value": float(reading.frequency_hz), "timestamp": now},
        )
    if reading.temperature_c is not None:
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="temperature",
            defaults={"value": float(reading.temperature_c), "timestamp": now},
        )
    if reading.soc_percent is not None:
        DeviceMetric.objects.create(
            device=device,
            metric_key="battery_soc",
            unit="%",
            value=float(reading.soc_percent),
            timestamp=now,
        )
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key="battery_soc",
            defaults={"value": float(reading.soc_percent), "timestamp": now},
        )

    # 5. Relais Schaltzustand
    if reading.relay_state is not None:
        try:
            cache.set(f"device:{device.id}:relay_state", reading.relay_state, timeout=3600)
        except Exception:
            pass

    # 6. Device Status aktualisieren
    device.last_seen = now
    device.active = True
    device.save(update_fields=["last_seen", "active"])

    return metrics
