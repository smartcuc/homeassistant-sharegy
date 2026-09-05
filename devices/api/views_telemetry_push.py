#######################################
# devices/api/views_telemetry_push.py
#######################################

import logging
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from devices.tasks import process_telemetry_push_async

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def telemetry_push(request):
    """
    Hochperformanter Telemetrie-Einspeisepunkt (asynchron via Celery / Redis).
    Akzeptiert einzelne oder gebündelte Messwerte (z. B. Shelly 3EM, Easee, Wärmepumpe).
    Entkoppelt den HTTP-Endpunkt vollständig von DB-I/O für maximale Durchsatzraten.
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
    now_iso = now.isoformat()
    force_sync = str(request.query_params.get("sync", "")).lower() in ("true", "1", "yes")

    import sys
    from django.conf import settings
    is_test = getattr(settings, "TESTING", False) or getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False) or any("test" in arg for arg in sys.argv)

    # 1. Asynchroner Pfad (Standard für maximale Geschwindigkeit & Skalierbarkeit in Produktion)
    if not force_sync and not is_test:
        try:
            task_res = process_telemetry_push_async.apply_async(
                args=[home.id, device_items, now_iso],
                queue="realtime",
            )
            return Response({
                "status": "success",
                "queued": True,
                "task_id": task_res.id,
                "devices_count": len(device_items),
                "timestamp": now_iso,
            })
        except Exception as e:
            logger.warning("Celery async dispatch failed for telemetry push, falling back to sync: %s", e)

    # 2. Synchroner Pfad (Fallback, Test-Runner oder expliziter Sync-Modus ?sync=true)
    result = process_telemetry_push_async(home.id, device_items, now_iso)
    return Response(result)


