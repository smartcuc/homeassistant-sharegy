#########################################
# devices/api/views_sungrow_webhook.py
#########################################

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.utils import timezone

from devices.models import Device, DeviceLatestMetric, CloudDeviceIntegration
from devices.services.ingest import broadcast_live_update

logger = logging.getLogger(__name__)


@csrf_exempt
def sungrow_webhook_receiver(request):
    """
    Offizieller Webhook-Empfänger für Sungrow iSolarCloud Event Message Subscriptions.
    Empfängt:
    - Challenge / URL-Verifikation (GET oder POST mit echostr / token)
    - Echtzeit-Störungsmeldungen & Alarme (Grid Under-Voltage, Inverter Fault, etc.)
    - Gerätestatus-Änderungen (Offline / Online / Recovery)
    """
    # 1. URL-Verifikation / Handshake von Sungrow Developer Portal
    if request.method == "GET":
        echostr = request.GET.get("echostr") or request.GET.get("echo") or request.GET.get("challenge")
        if echostr:
            logger.info("[Sungrow-Webhook] Challenge Handshake verifiziert: %s", echostr)
            return HttpResponse(echostr, content_type="text/plain")
        return JsonResponse({"status": "ok", "service": "Sharegy Sungrow Webhook Receiver"})

    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    # 2. Payload parsen
    try:
        body = request.body.decode("utf-8")
        data = json.loads(body) if body else {}
    except Exception as e:
        logger.warning("[Sungrow-Webhook] Ungültiger JSON Body: %s", e)
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    # Sungrow schickt manche Verifikationen als POST JSON mit echostr
    if "echostr" in data:
        logger.info("[Sungrow-Webhook] POST Challenge Handshake verifiziert: %s", data["echostr"])
        return JsonResponse({"echostr": data["echostr"]})

    logger.info("[Sungrow-Webhook] Event empfangen: %s", json.dumps(data)[:300])

    # 3. Ereignis-Parameter extrahieren
    # Sungrow Payload Formate variieren leicht je nach Firmware/API-Version:
    ps_id = str(data.get("ps_id") or data.get("psId") or data.get("data", {}).get("ps_id") or "")
    sn = str(data.get("sn") or data.get("device_sn") or data.get("data", {}).get("device_sn") or "")
    event_type = str(data.get("event_type") or data.get("msg_type") or "alarm").lower()

    fault_code = (
        data.get("fault_code")
        or data.get("faultCode")
        or data.get("data", {}).get("fault_code")
        or data.get("code")
    )
    fault_name = (
        data.get("fault_name")
        or data.get("faultName")
        or data.get("data", {}).get("fault_name")
        or data.get("message")
        or "Gerätestörung"
    )
    fault_level = str(
        data.get("fault_level")
        or data.get("faultLevel")
        or data.get("data", {}).get("fault_level")
        or "warning"
    ).lower()

    # Status: 1 = aufgetreten/aktiv (occurred), 2 = behoben/recovered
    status_raw = data.get("status") or data.get("data", {}).get("status")
    is_recovered = (
        str(status_raw).lower() in ["2", "recovered", "cleared", "resolved", "0"]
        or "recover" in str(fault_name).lower()
    )

    # 4. Passendes Gerät in Sharegy identifizieren
    target_device = None
    target_integration = None

    if ps_id:
        integrations = CloudDeviceIntegration.objects.filter(
            profile_id="sungrow_isolarcloud",
            is_active=True,
        ).select_related("device", "device__home")
        for integ in integrations:
            creds = integ.credentials or {}
            c_ps = str(creds.get("ps_id") or creds.get("ps_ids") or "")
            if ps_id in c_ps or (c_ps and c_ps in ps_id):
                target_device = integ.device
                target_integration = integ
                break

    if not target_device and sn:
        target_device = Device.objects.filter(
            identifier__icontains=sn,
            active=True,
            pending_delete=False,
        ).first()

    if not target_device:
        # Fallback auf erstes aktives Sungrow Gerät
        target_integration = CloudDeviceIntegration.objects.filter(
            profile_id="sungrow_isolarcloud",
            is_active=True,
        ).select_related("device").first()
        if target_integration:
            target_device = target_integration.device

    if not target_device:
        logger.warning("[Sungrow-Webhook] Kein passendes Gerät für ps_id=%s, sn=%s gefunden", ps_id, sn)
        return JsonResponse({"status": "ignored", "reason": "No matching device found"})

    now = timezone.now()
    alarm_cache_key = f"device:{target_device.id}:sungrow_alarm"

    # 5. System-Health & Alarmstatus aktualisieren
    if is_recovered or (fault_code == 0 and not is_recovered):
        # Störung behoben
        logger.info("[Sungrow-Webhook] ✅ Störung behoben für Gerät %s (%s)", target_device.id, fault_name)
        cache.delete(alarm_cache_key)

        DeviceLatestMetric.objects.update_or_create(
            device=target_device,
            metric_key="state.alarm",
            defaults={
                "value": 0.0,
                "unit": "",
                "data": {"status": "ok", "cleared_at": now.isoformat()},
                "timestamp": now,
            },
        )
    else:
        # Neue Störung / Alarm aktiv
        logger.warning("[Sungrow-Webhook] 🚨 Aktive Störung für Gerät %s: Code %s - %s", target_device.id, fault_code, fault_name)
        alarm_payload = {
            "device_id": target_device.id,
            "device_name": target_device.name or target_device.identifier,
            "code": fault_code,
            "name": fault_name,
            "level": fault_level,
            "timestamp": now.isoformat(),
        }
        cache.set(alarm_cache_key, alarm_payload, timeout=86400 * 3)  # 3 Tage persistieren bis Reset

        DeviceLatestMetric.objects.update_or_create(
            device=target_device,
            metric_key="state.alarm",
            defaults={
                "value": float(fault_code or 1),
                "unit": "",
                "data": alarm_payload,
                "timestamp": now,
            },
        )
        DeviceLatestMetric.objects.update_or_create(
            device=target_device,
            metric_key="state.fault_name",
            defaults={
                "value": None,
                "unit": "",
                "data": {"fault_name": fault_name, "level": fault_level},
                "timestamp": now,
            },
        )

    # 6. Live WebSocket Broadcast für sofortige Dashboard-Aktualisierung
    try:
        broadcast_live_update(
            target_device,
            "system_health_update",
            0.0 if is_recovered else float(fault_code or 1),
            "",
            now,
        )
    except Exception:
        pass

    return JsonResponse({
        "status": "success",
        "device_id": target_device.id,
        "is_recovered": is_recovered,
        "fault_code": fault_code,
    })
