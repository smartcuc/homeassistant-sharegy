#################
# tracking/api.py
#################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db import models
from django.utils import timezone
from datetime import timedelta

from .services import track_event
from .analytics import get_kpis, get_funnel, _base_queryset
from .models import EventLog


# ============================================================
# ✅ TRACK SINGLE EVENT
# ============================================================

class TrackEventView(APIView):
    def post(self, request):
        events = request.data.get("events")
        if isinstance(events, list):
            for e in events:
                name = e.get("name") or e.get("event")
                if name:
                    track_event(
                        name=name,
                        metadata=e.get("metadata", {}),
                        request=request,
                    )
            return Response({"ok": True})

        name = request.data.get("name") or request.data.get("event")
        metadata = request.data.get("metadata", {})

        if not name:
            return Response({"error": "missing event name"}, status=400)

        track_event(
            name=name,
            metadata=metadata,
            request=request,
        )

        return Response({"ok": True})


# ============================================================
# ✅ TRACK BATCH EVENTS
# ============================================================

class TrackEventBatchView(APIView):
    def post(self, request):
        events = request.data.get("events", [])

        if not isinstance(events, list):
            return Response({"error": "events must be a list"}, status=400)

        for e in events:
            name = e.get("name") or e.get("event")

            if not name:
                continue  # skip invalid

            track_event(
                name=name,
                metadata=e.get("metadata", {}),
                request=request,
            )

        return Response({"ok": True})


# ============================================================
# ✅ KPI & STATS VIEW
# ============================================================

class KPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Tenant ermitteln falls vorhanden (z.B. User-Mitgliedschaft)
        tenant = getattr(request.user, "tenant", None)
        if not tenant and hasattr(request.user, "memberships"):
            first_m = request.user.memberships.select_related("tenant").first()
            if first_m:
                tenant = first_m.tenant

        context = "tenant" if tenant and not (request.user.is_staff or request.user.is_superuser) else "global"

        try:
            days = int(request.GET.get("days", 7))
        except (TypeError, ValueError):
            days = 7

        now = timezone.now()
        window_start = now - timedelta(days=days)

        # Base QuerySet
        base_qs = _base_queryset(tenant=tenant, context=context)

        # 1. KPIs
        kpis = get_kpis(tenant=tenant, context=context, days=days)

        # 2. Stats gruppiert nach Event-Name
        stats_qs = (
            base_qs.filter(created_at__gte=window_start)
            .values("name")
            .annotate(count=models.Count("id"))
            .order_by("-count")
        )
        stats = [{"event": item["name"], "count": item["count"]} for item in stats_qs]

        # 3. Daily Events (für 7-Tage Timeline)
        daily_qs = (
            base_qs.filter(created_at__gte=window_start)
            .annotate(date=models.functions.TruncDate("created_at"))
            .values("date")
            .annotate(count=models.Count("id"))
            .order_by("date")
        )
        daily = [
            {
                "date": item["date"].strftime("%Y-%m-%d") if hasattr(item["date"], "strftime") else str(item["date"]),
                "count": item["count"]
            }
            for item in daily_qs
        ]

        funnel_data = get_funnel(tenant=tenant, context=context, days=days)

        return Response({
            **kpis,
            "stats": stats,
            "daily": daily,
            "funnel": funnel_data.get("steps", []),
            "total_events": sum(s["count"] for s in stats),
        })


# ============================================================
# ✅ FUNNEL VIEW
# ============================================================

class FunnelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = getattr(request.user, "tenant", None)
        if not tenant and hasattr(request.user, "memberships"):
            first_m = request.user.memberships.select_related("tenant").first()
            if first_m:
                tenant = first_m.tenant

        context = "tenant" if tenant and not (request.user.is_staff or request.user.is_superuser) else "global"

        try:
            days = int(request.GET.get("days", 7))
        except (TypeError, ValueError):
            days = 7

        return Response(
            get_funnel(
                tenant=tenant,
                context=context,
                days=days
            )
        )