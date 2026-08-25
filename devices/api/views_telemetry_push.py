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

    for item in device_items:
        identifier = str(item.get("identifier") or item.get("id") or "").strip()
        if not identifier:
            continue

        name = item.get("name") or identifier
        power_w = item.get("power_w") or item.get("power") or item.get("value")
        energy_kwh = item.get("energy_kwh") or item.get("energy")
        role_key = item.get("role") or "consumer"

        # 1. Device ermitteln oder automatisch registrieren
        dev, created = Device.objects.get_or_create(
            home=home,
            identifier=identifier,
            defaults={
                "configured": True,
                "active": True,
            },
        )

        # 2. Config & Role anlegen falls neu
        if created or not getattr(dev, "config", None):
            role_obj = DeviceRole.objects.filter(key=role_key).first()
            if not role_obj:
                role_obj = DeviceRole.objects.filter(key="consumer").first()

            DeviceConfig.objects.update_or_create(
                device=dev,
                defaults={
                    "home": home,
                    "name": name,
                    "role": role_obj,
                },
            )

        # 3. Latest Metric (Live-Leistung) aktualisieren
        if power_w is not None:
            try:
                val_float = float(power_w)
                DeviceLatestMetric.objects.update_or_create(
                    device=dev,
                    metric_key="power",
                    defaults={
                        "value": val_float,
                        "timestamp": now,
                    },
                )
                saved_count += 1
            except (ValueError, TypeError):
                pass

        # 4. Stunden-Aggregat für Historie / 1h-Bucket updaten
        if power_w is not None or energy_kwh is not None:
            bucket_dt = now.replace(minute=0, second=0, microsecond=0)
            avg_w = float(power_w) if power_w is not None else 0.0
            energy_wh = float(energy_kwh) * 1000.0 if energy_kwh is not None else (avg_w * 1.0)

            DeviceMetric1h.objects.update_or_create(
                device=dev,
                bucket=bucket_dt,
                defaults={
                    "avg": avg_w,
                    "energy_wh": energy_wh,
                },
            )

        updated_devices.append(identifier)

    return Response({
        "status": "success",
        "saved_metrics": saved_count,
        "devices_updated": updated_devices,
        "timestamp": now.isoformat(),
    })

