###################
# alerts/views.py
###################

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from alerts.models import AlertEvent
from alerts.services import evaluate_home_alerts


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def alerts_list(request):
    home = request.user.homes.first() if hasattr(request.user, "homes") else None
    if not home:
        return Response({
            "summary": {"critical": 0, "warning": 0, "info": 0, "active_total": 0},
            "alerts": [],
        })

    # Führe Live-Regelauswertung aus
    evaluate_home_alerts(home)

    # Lade alle aktiven und zuletzt gelösten Alarme (letzte 20)
    qs = AlertEvent.objects.filter(home=home).order_by("-created_at")[:20]

    alerts_data = []
    critical_count = 0
    warning_count = 0
    info_count = 0
    active_total = 0

    for a in qs:
        is_active = (a.status in [AlertEvent.STATUS_ACTIVE, AlertEvent.STATUS_ACKNOWLEDGED])
        if is_active:
            active_total += 1
            if a.severity == AlertEvent.SEVERITY_CRITICAL:
                critical_count += 1
            elif a.severity == AlertEvent.SEVERITY_WARNING:
                warning_count += 1
            elif a.severity == AlertEvent.SEVERITY_INFO:
                info_count += 1

        alerts_data.append({
            "id": str(a.id),
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "action_hint": a.action_hint,
            "action_type": a.action_type,
            "details": a.details,
            "status": a.status,
            "created_at": a.created_at.isoformat(),
            "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
        })

    return Response({
        "summary": {
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count,
            "active_total": active_total,
        },
        "alerts": alerts_data,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def acknowledge_alert(request, alert_id):
    home = request.user.homes.first() if hasattr(request.user, "homes") else None
    if not home:
        return Response({"error": "No home found"}, status=400)

    try:
        alert = AlertEvent.objects.get(id=alert_id, home=home)
        alert.status = AlertEvent.STATUS_ACKNOWLEDGED
        alert.acknowledged_at = timezone.now()
        alert.save(update_fields=["status", "acknowledged_at"])
        return Response({"status": "acknowledged", "id": str(alert.id)})
    except AlertEvent.DoesNotExist:
        return Response({"error": "Alert not found"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resolve_alert(request, alert_id):
    home = request.user.homes.first() if hasattr(request.user, "homes") else None
    if not home:
        return Response({"error": "No home found"}, status=400)

    try:
        alert = AlertEvent.objects.get(id=alert_id, home=home)
        alert.status = AlertEvent.STATUS_RESOLVED
        alert.resolved_at = timezone.now()
        alert.save(update_fields=["status", "resolved_at"])
        return Response({"status": "resolved", "id": str(alert.id)})
    except AlertEvent.DoesNotExist:
        return Response({"error": "Alert not found"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def seed_demo_alerts(request):
    home = request.user.homes.first() if hasattr(request.user, "homes") else None
    if not home:
        return Response({"error": "No home found"}, status=400)

    AlertEvent.objects.filter(home=home).delete()

    sample_alerts = [
        AlertEvent(
            home=home,
            alert_type="negative_price",
            severity=AlertEvent.SEVERITY_INFO,
            title="Börsenstrom-Tiefstpreis (Spar-Chance)",
            message="Günstiger Börsenstrom von 13:00 bis 16:00 Uhr (12,4 ct/kWh brutto). Starte deine Wallbox oder Großverbraucher in diesem Zeitfenster.",
            action_hint="Ladefenster im Optimizer ansehen",
            action_type="open_optimizer",
            status=AlertEvent.STATUS_ACTIVE,
        ),
        AlertEvent(
            home=home,
            alert_type="battery_empty",
            severity=AlertEvent.SEVERITY_CRITICAL,
            title="Batterie leer / Notstromreserve erreicht",
            message="Der Ladestand des Hausspeichers liegt bei 8.5 % (Notstromreserve). Die Batterie wird bei günstigem Strompreis nachgeladen.",
            action_hint="Speicher-Ladung konfigurieren",
            action_type="charge_battery",
            status=AlertEvent.STATUS_ACTIVE,
        ),
        AlertEvent(
            home=home,
            alert_type="price_peak",
            severity=AlertEvent.SEVERITY_WARNING,
            title="Hohe Preisspitze an der Strombörse (42 ct/kWh)",
            message="Um 19:00 Uhr wird ein Peak von 42,8 ct/kWh erwartet. Schalte flexible Verbraucher ab und nutze den Hausspeicher.",
            action_hint="Großverbraucher pausieren",
            action_type="pause_loads",
            status=AlertEvent.STATUS_ACTIVE,
        ),
    ]

    AlertEvent.objects.bulk_create(sample_alerts)
    return Response({"status": "ok", "created": len(sample_alerts)})

