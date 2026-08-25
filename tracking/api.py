#################
# tracking/api.py
#################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import track_event
from .analytics import get_kpis, get_funnel


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
# ✅ KPI VIEW
# ============================================================

class KPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = getattr(request.user, "tenant", None)

        if not tenant:
            return Response({"error": "no tenant"}, status=400)

        # ✅ flexibel über Query Param
        try:
            days = int(request.GET.get("days", 7))
        except ValueError:
            return Response({"error": "invalid days parameter"}, status=400)

        return Response(
            get_kpis(
                tenant=tenant,
                context="tenant",
                days=days
            )
        )


# ============================================================
# ✅ FUNNEL VIEW
# ============================================================

class FunnelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = getattr(request.user, "tenant", None)

        if not tenant:
            return Response({"error": "no tenant"}, status=400)

        try:
            days = int(request.GET.get("days", 7))
        except ValueError:
            return Response({"error": "invalid days parameter"}, status=400)

        return Response(
            get_funnel(
                tenant=tenant,
                context="tenant",
                days=days
            )
        )
    