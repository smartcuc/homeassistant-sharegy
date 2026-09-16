"""
vpp/views.py

REST-API Endpunkte für das Virtuelle Kraftwerk (VPP) und Übertragungsnetzbetreiber (ÜNB/VNB):
- Sekundärregelleistung (aFRR), FCR und Redispatch 2.0
- Flexibilitätsaggregation, 96-Viertelstunden-Fahrpläne
- Dispatch-Steuerung & Telemetrie-Erbringungsnachweise
"""

from decimal import Decimal
from datetime import date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone

from vpp.models import VPPFlexibilityPool, VPPDispatchOrder, VPPDispatchTelemetry
from vpp.services_vpp import (
    calculate_fleet_flexibility,
    generate_redispatch_schedule_15min,
    trigger_vpp_dispatch,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vpp_fleet_summary_view(request):
    """
    Liefert die aggregierten VPP-Kennzahlen (Gesamtkapazität, aktive Flexibilität, Reaktionszeit).
    """
    tso = request.GET.get("tso")
    plz = request.GET.get("plz")
    data = calculate_fleet_flexibility(tso_operator=tso, postal_code_prefix=plz)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vpp_flexibility_view(request):
    """
    Echtzeit-Flexibilitätsband (+kW / -kW) für Regelleistungsmärkte und Netzbetreiber.
    """
    tso = request.GET.get("tso")
    plz = request.GET.get("plz")
    data = calculate_fleet_flexibility(tso_operator=tso, postal_code_prefix=plz)
    return Response({
        "timestamp": data["timestamp"],
        "available_positive_power_kw": data["summary"]["total_available_positive_flex_kw"],
        "available_negative_power_kw": data["summary"]["total_available_negative_flex_kw"],
        "battery_stored_kwh": data["battery_fleet"]["total_stored_energy_kwh"],
        "battery_capacity_kwh": data["battery_fleet"]["total_capacity_kwh"],
        "average_soc_pct": data["battery_fleet"]["average_soc_pct"],
        "controllable_loads_kw": data["steuve_and_loads"]["curtailable_power_kw"],
        "pv_curtailable_kw": data["pv_curtailment"]["curtailable_power_kw"],
        "market_products": ["aFRR", "FCR", "Redispatch 2.0"],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vpp_redispatch_schedule_view(request):
    """
    Liefert den 96-Viertelstunden-Fahrplan für Redispatch 2.0 / Connect+ für einen Zieldurchlauftag.
    """
    date_str = request.GET.get("date")
    tso = request.GET.get("tso", "50hertz")
    
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return Response({"error": "Invalid date format, expected YYYY-MM-DD"}, status=400)
    else:
        target_date = timezone.now().date()

    schedule = generate_redispatch_schedule_15min(target_date=target_date, tso_operator=tso)
    return Response(schedule)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def vpp_pools_view(request):
    """
    GET: Liste aller registrierten Flexibilitäts-Pools
    POST: Neuen VPP-Pool anlegen
    """
    if request.method == "GET":
        pools = VPPFlexibilityPool.objects.filter(is_active=True).order_by("name")
        res = [
            {
                "id": str(p.id),
                "name": p.name,
                "tso_operator": p.tso_operator,
                "market_product": p.market_product,
                "grid_region": p.grid_region,
                "postal_code_prefix": p.postal_code_prefix,
                "min_activation_power_kw": float(p.min_activation_power_kw),
                "max_activation_power_kw": float(p.max_activation_power_kw),
                "is_active": p.is_active,
                "orders_count": p.dispatch_orders.count(),
            }
            for p in pools
        ]
        return Response({"count": len(res), "pools": res})

    elif request.method == "POST":
        name = request.data.get("name")
        if not name:
            return Response({"error": "name is required"}, status=400)

        pool = VPPFlexibilityPool.objects.create(
            name=name,
            tso_operator=request.data.get("tso_operator", "50hertz"),
            market_product=request.data.get("market_product", "afrr_positive"),
            grid_region=request.data.get("grid_region", "Deutschland"),
            postal_code_prefix=request.data.get("postal_code_prefix", "*"),
            min_activation_power_kw=Decimal(str(request.data.get("min_activation_power_kw", 1.0))),
            max_activation_power_kw=Decimal(str(request.data.get("max_activation_power_kw", 500.0))),
            is_active=True,
        )
        return Response({"id": str(pool.id), "name": pool.name, "created": True}, status=201)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def vpp_dispatch_orders_view(request):
    """
    GET: Liste aller Dispatch-Aufträge und Aktivierungen
    POST: Neuen Abruf (Dispatch) von Regelleistung oder Redispatch auslösen
    """
    if request.method == "GET":
        orders = VPPDispatchOrder.objects.all().order_by("-created_at")[:50]
        res = [
            {
                "id": str(o.id),
                "dispatch_type": o.dispatch_type,
                "target_power_kw": float(o.target_power_kw),
                "duration_minutes": o.duration_minutes,
                "status": o.status,
                "requested_by": o.requested_by,
                "connect_plus_order_id": o.connect_plus_order_id,
                "start_time": o.start_time.isoformat() if o.start_time else None,
                "end_time": o.end_time.isoformat() if o.end_time else None,
                "delivered_power_kw": float(o.delivered_power_kw),
                "energy_delivered_kwh": float(o.energy_delivered_kwh),
                "remuneration_eur": float(o.remuneration_eur),
                "activated_devices_count": o.activated_devices_count,
            }
            for o in orders
        ]
        return Response({"count": len(res), "orders": res})

    elif request.method == "POST":
        target_kw = request.data.get("target_power_kw")
        if not target_kw:
            return Response({"error": "target_power_kw is required"}, status=400)

        try:
            target_kw_dec = Decimal(str(target_kw))
        except Exception:
            return Response({"error": "Invalid target_power_kw"}, status=400)

        duration = int(request.data.get("duration_minutes", 15))
        dispatch_type = request.data.get("dispatch_type", "positive_flex")
        requested_by = request.data.get("requested_by", "TenneT Leitsystem")
        pool_id = request.data.get("pool_id")
        pool = VPPFlexibilityPool.objects.filter(id=pool_id).first() if pool_id else None

        order = trigger_vpp_dispatch(
            target_power_kw=target_kw_dec,
            duration_minutes=duration,
            dispatch_type=dispatch_type,
            requested_by=requested_by,
            pool=pool,
        )

        return Response({
            "id": str(order.id),
            "status": order.status,
            "dispatch_type": order.dispatch_type,
            "target_power_kw": float(order.target_power_kw),
            "duration_minutes": order.duration_minutes,
            "connect_plus_order_id": order.connect_plus_order_id,
            "start_time": order.start_time.isoformat(),
            "end_time": order.end_time.isoformat() if order.end_time else None,
            "activated_devices_count": order.activated_devices_count,
            "message": "Dispatch successfully activated across fleet assets.",
        }, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vpp_dispatch_order_detail_view(request, order_id):
    """
    Detaillierte Telemetrie und Erfüllungsgrad eines Abruf-Auftrags.
    """
    order = VPPDispatchOrder.objects.filter(id=order_id).first()
    if not order:
        return Response({"error": "Dispatch order not found"}, status=404)

    telemetry = order.telemetry_points.all().order_by("timestamp")
    telemetry_list = [
        {
            "timestamp": t.timestamp.isoformat(),
            "target_power_kw": float(t.target_power_kw),
            "measured_power_kw": float(t.measured_power_kw),
            "frequency_hz": float(t.frequency_hz),
            "battery_soc_avg": float(t.battery_soc_avg),
        }
        for t in telemetry
    ]

    fulfillment_pct = (
        float((order.delivered_power_kw / order.target_power_kw * 100).quantize(Decimal("0.1")))
        if order.target_power_kw > 0
        else 100.0
    )

    return Response({
        "id": str(order.id),
        "status": order.status,
        "dispatch_type": order.dispatch_type,
        "target_power_kw": float(order.target_power_kw),
        "delivered_power_kw": float(order.delivered_power_kw),
        "energy_delivered_kwh": float(order.energy_delivered_kwh),
        "fulfillment_rate_pct": fulfillment_pct,
        "remuneration_eur": float(order.remuneration_eur),
        "start_time": order.start_time.isoformat() if order.start_time else None,
        "end_time": order.end_time.isoformat() if order.end_time else None,
        "activated_devices_count": order.activated_devices_count,
        "meta_info": order.meta_info,
        "telemetry_points_count": len(telemetry_list),
        "telemetry": telemetry_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vpp_dispatch_order_cancel_view(request, order_id):
    """
    Stornierung / vorzeitiger Rückruf eines Dispatch-Auftrags.
    """
    order = VPPDispatchOrder.objects.filter(id=order_id).first()
    if not order:
        return Response({"error": "Dispatch order not found"}, status=404)

    order.status = "cancelled"
    order.end_time = timezone.now()
    order.save()

    return Response({
        "id": str(order.id),
        "status": order.status,
        "message": "Dispatch order cancelled successfully.",
    })


# ---------------------------------------------------------------------------
# 👥 Endkunden- & Teilnehmer-Endpunkte (Opt-In, Flexibilitäts-Dashboard & Erlöse)
# ---------------------------------------------------------------------------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def vpp_user_enrollments_view(request):
    """
    GET: Liste aller eingeschriebenen Geräte des Nutzers
    POST: Gerät (Batteriespeicher, Wallbox, § 14a WP) in das VPP einschreiben
    """
    from vpp.services_clearing import enroll_device_in_vpp, get_user_flexibility_summary

    if request.method == "GET":
        summary = get_user_flexibility_summary(request.user)
        return Response(summary)

    # POST: Einschreibung
    data = request.data
    device_id = data.get("device_id")
    if not device_id:
        return Response({"error": "device_id is required"}, status=400)

    pool_id = data.get("pool_id")
    min_soc = Decimal(str(data.get("min_soc_reserve_pct", "20.00")))
    auto_spot = bool(data.get("auto_spot_arbitrage", True))
    auto_afrr = bool(data.get("auto_afrr_frequency", True))

    try:
        enrollment = enroll_device_in_vpp(
            user=request.user,
            device_id=int(device_id),
            pool_id=pool_id,
            min_soc_reserve_pct=min_soc,
            auto_spot_arbitrage=auto_spot,
            auto_afrr_frequency=auto_afrr,
        )
        return Response({
            "message": "Asset successfully enrolled in VPP.",
            "enrollment_id": str(enrollment.id),
            "device_id": enrollment.device_id,
            "status": enrollment.status,
            "min_soc_reserve_pct": float(enrollment.min_soc_reserve_pct),
            "payout_share_pct": float(enrollment.payout_share_pct),
        }, status=201)
    except PermissionError as pe:
        return Response({"error": str(pe)}, status=403)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(["PATCH", "POST"])
@permission_classes([IsAuthenticated])
def vpp_user_enrollment_detail_view(request, enrollment_id):
    """
    Status ändern (active / paused / opted_out) oder Mindest-SoC anpassen.
    """
    from vpp.services_clearing import set_enrollment_status
    from vpp.models import VPPAssetEnrollment

    qs = VPPAssetEnrollment.objects.filter(id=enrollment_id)
    if not request.user.is_staff:
        qs = qs.filter(user=request.user)
    enrollment = qs.first()
    if not enrollment:
        return Response({"error": "Enrollment not found"}, status=404)

    data = request.data
    if "status" in data:
        enrollment = set_enrollment_status(request.user, str(enrollment.id), data["status"])

    if "min_soc_reserve_pct" in data:
        try:
            val = Decimal(str(data["min_soc_reserve_pct"]))
            enrollment.min_soc_reserve_pct = max(Decimal("10.00"), min(Decimal("60.00"), val))
            enrollment.save(update_fields=["min_soc_reserve_pct", "updated_at"])
        except Exception:
            pass

    return Response({
        "id": str(enrollment.id),
        "device_id": enrollment.device_id,
        "status": enrollment.status,
        "min_soc_reserve_pct": float(enrollment.min_soc_reserve_pct),
        "total_earned_eur": float(enrollment.total_earned_eur),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vpp_user_earnings_view(request):
    """
    Erlösübersicht, getätigte Abrufe und Clearing Statements für den eingeloggten Kunden.
    """
    from vpp.services_clearing import get_user_flexibility_summary
    data = get_user_flexibility_summary(request.user)
    return Response(data)


# ---------------------------------------------------------------------------
# ⚖️ Monetäres Clearing & Abrechnungs-Endpunkte
# ---------------------------------------------------------------------------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def vpp_clearing_run_view(request):
    """
    GET: Letzte Clearing-Abrechnungen (Admin/Staff)
    POST: Periodischen Clearing-Lauf ausführen
    """
    from vpp.models import VPPClearingStatement
    from vpp.services_clearing import execute_periodic_clearing_run

    if request.method == "GET":
        qs = VPPClearingStatement.objects.all().order_by("-period_end")[:50]
        if not request.user.is_staff:
            qs = qs.filter(user=request.user)
        res = [
            {
                "id": str(s.id),
                "user_email": s.user.email,
                "period_start": s.period_start.isoformat(),
                "period_end": s.period_end.isoformat(),
                "dispatches_count": s.dispatches_count,
                "total_energy_kwh": float(s.total_energy_kwh),
                "gross_revenue_eur": float(s.gross_revenue_eur),
                "customer_payout_eur": float(s.customer_payout_eur),
                "sharegy_fee_eur": float(s.sharegy_fee_eur),
                "status": s.status,
                "payment_reference": s.payment_reference,
                "credited_at": s.credited_at.isoformat() if s.credited_at else None,
            }
            for s in qs
        ]
        return Response({"statements": res})

    # POST: Nur Staff darf Clearing-Lauf auslösen
    if not request.user.is_staff:
        return Response({"error": "Admin privileges required to trigger clearing run"}, status=403)

    p_start_str = request.data.get("period_start")
    p_end_str = request.data.get("period_end")

    p_start = date.fromisoformat(p_start_str) if p_start_str else None
    p_end = date.fromisoformat(p_end_str) if p_end_str else None

    statements = execute_periodic_clearing_run(period_start=p_start, period_end=p_end)
    return Response({
        "message": f"Clearing run completed. Generated {len(statements)} statements.",
        "statements_count": len(statements),
        "total_customer_payout_eur": float(sum(s.customer_payout_eur for s in statements)),
        "total_sharegy_fee_eur": float(sum(s.sharegy_fee_eur for s in statements)),
    })


# ---------------------------------------------------------------------------
# 🔌 Externe Aggregator / ÜNB Webhook Schnittstelle (Next Kraftwerke, Entelios, Connect+)
# ---------------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def vpp_aggregator_webhook_view(request):
    """
    Standardisierter Webhook für autorisierte externe Aggregatoren und ÜNBs
    (z. B. Next Kraftwerke / 50Hertz Connect+ / EnSpire API).
    """
    from django.conf import settings
    
    # Header-Token prüfen
    auth_header = request.headers.get("X-VPP-API-KEY") or request.headers.get("Authorization", "")
    expected_token = getattr(settings, "VPP_AGGREGATOR_API_KEY", "sharegy-vpp-secure-key-2026")
    
    if not auth_header or (expected_token not in auth_header and f"Bearer {expected_token}" != auth_header):
        return Response({"error": "Unauthorized aggregator access"}, status=401)

    data = request.data
    target_power_kw = Decimal(str(data.get("target_power_kw", "50.0")))
    duration_min = int(data.get("duration_minutes", 15))
    dispatch_type = data.get("dispatch_type", "positive_flex")
    requested_by = data.get("requested_by", "External Grid Aggregator")
    pool_id = data.get("pool_id")

    pool = VPPFlexibilityPool.objects.filter(id=pool_id).first() if pool_id else None

    order = trigger_vpp_dispatch(
        target_power_kw=target_power_kw,
        duration_minutes=duration_min,
        dispatch_type=dispatch_type,
        requested_by=requested_by,
        pool=pool,
    )

    return Response({
        "status": "accepted",
        "order_id": str(order.id),
        "connect_plus_order_id": order.connect_plus_order_id,
        "target_power_kw": float(order.target_power_kw),
        "activated_devices_count": order.activated_devices_count,
        "remuneration_eur": float(order.remuneration_eur),
        "estimated_ramp_up_sec": 15,
    }, status=202)

