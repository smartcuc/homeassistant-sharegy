#######################################
# devices/api/views_telemetry_push.py
#######################################

from datetime import datetime
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from devices.models import Device, DeviceLatestMetric, DeviceMetric1h, DeviceConfig, DeviceRole, MetricDefinition


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def telemetry_push(request):
    """
    Sicherer Batch-Telemetrie-Einspeisepunkt für Home Assistant und externe Smart-Home-Bridges.
    Akzeptiert einzelne oder gebündelte Messwerte (z. B. Shelly 3EM, Easee, Wärmepumpe).
    """
    data = request.data or {}
    home = request.user.homes.first() if hasattr(request.user, "homes") else None

    if not home:
        return Response({"status": "error", "message": "Kein Home für diesen Benutzer hinterlegt."}, status=400)

    # Akzeptiert Liste oder dict mit "devices"
    device_items = data.get("devices", [])
    if isinstance(data, list):
        device_items = data
    elif not device_items and "identifier" in data:
        device_items = [data]

    if not device_items:
        return Response({"status": "error", "message": "Keine Gerätemesswerte übergeben."}, status=400)

    now = timezone.now()
    saved_count = 0
    updated_devices = []

    # 1. Vorhandene Geräte des Haushalts in einem einzigen Query laden
    existing_devs = {
        dev.identifier: dev
        for dev in Device.objects.filter(home=home).select_related("config")
    }

    latest_metrics_to_upsert = []
    hourly_metrics_to_upsert = []
    bucket_dt = now.replace(minute=0, second=0, microsecond=0)

    for item in device_items:
        identifier = str(item.get("identifier") or item.get("id") or "").strip()
        if not identifier:
            continue

        name = item.get("name") or identifier
        power_w = item.get("power_w") or item.get("power") or item.get("value")
        energy_kwh = item.get("energy_kwh") or item.get("energy")
        role_key = item.get("role") or "consumer"

        # 1. Device aus Cache oder neu anlegen
        dev = existing_devs.get(identifier)
        if not dev:
            dev, _ = Device.objects.get_or_create(
                home=home,
                identifier=identifier,
                defaults={
                    "configured": True,
                    "active": True,
                },
            )
            existing_devs[identifier] = dev

        # 2. Config falls nötig anlegen
        if not getattr(dev, "config", None):
            role_obj = DeviceRole.objects.filter(key=role_key).first() or DeviceRole.objects.filter(key="consumer").first()
            DeviceConfig.objects.update_or_create(
                device=dev,
                defaults={
                    "home": home,
                    "name": name,
                    "role": role_obj,
                },
            )

        # 3. Latest Metric (Live-Leistung)
        if power_w is not None:
            try:
                val_float = float(power_w)
                latest_metrics_to_upsert.append(
                    DeviceLatestMetric(
                        device=dev,
                        metric_key="power",
                        value=val_float,
                        unit="W",
                        timestamp=now,
                    )
                )
                saved_count += 1
            except (ValueError, TypeError):
                pass

        # 4. Stunden-Aggregat
        if power_w is not None or energy_kwh is not None:
            avg_w = float(power_w) if power_w is not None else 0.0
            energy_wh = float(energy_kwh) * 1000.0 if energy_kwh is not None else (avg_w * 1.0)
            hourly_metrics_to_upsert.append(
                DeviceMetric1h(
                    device=dev,
                    metric_key="power",
                    bucket=bucket_dt,
                    avg=avg_w,
                    min=avg_w,
                    max=avg_w,
                    count=1,
                    energy_wh=energy_wh,
                )
            )

        updated_devices.append(identifier)

    # High-Performance Batch Upserts
    if latest_metrics_to_upsert:
        DeviceLatestMetric.objects.bulk_create(
            latest_metrics_to_upsert,
            update_conflicts=True,
            unique_fields=["device", "metric_key"],
            update_fields=["value", "unit", "timestamp"],
        )

    if hourly_metrics_to_upsert:
        DeviceMetric1h.objects.bulk_create(
            hourly_metrics_to_upsert,
            update_conflicts=True,
            unique_fields=["device", "metric_key", "bucket"],
            update_fields=["avg", "min", "max", "energy_wh"],
        )

    return Response({
        "status": "success",
        "saved_metrics": saved_count,
        "devices_updated": updated_devices,
        "timestamp": now.isoformat(),
    })

