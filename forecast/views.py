###################
# forecast/views.py
###################

from datetime import timedelta
from collections import defaultdict

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Tenant
from devices.models import Home
from producer.models import GeneratorString
from forecast.models import SolarForecast

VALID_SOURCES = {"ml", "physics", "hybrid"}


def _parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _get_tenant_or_error(request):
    tenant_id = request.GET.get("tenant")

    if not tenant_id:
        return None, Response(
            {"error": "tenant query parameter is required"},
            status=400,
        )

    try:
        tenant = Tenant.objects.get(id=tenant_id)
        return tenant, None
    except Tenant.DoesNotExist:
        return None, Response({"error": "tenant not found"}, status=404)


def _ceil_to_next_hour(dt):
    dt = dt.replace(second=0, microsecond=0)

    if dt.minute == 0:
        return dt

    return (dt + timedelta(hours=1)).replace(minute=0)


# =========================================================
# FORECAST LIST
# GET /api/forecast/?tenant=<uuid>&source=hybrid&hours=24&limit=100&offset=0
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def forecast_list(request):
    tenant, error = _get_tenant_or_error(request)
    if error:
        return error

    source = request.GET.get("source", "hybrid")
    hours = _parse_int(request.GET.get("hours"), 24)
    limit = _parse_int(request.GET.get("limit"), 100)
    offset = _parse_int(request.GET.get("offset"), 0)

    if source not in VALID_SOURCES:
        return Response(
            {
                "error": f"invalid source '{source}'",
                "valid_sources": sorted(VALID_SOURCES),
            },
            status=400,
        )

    now = _ceil_to_next_hour(timezone.now())
    end = now + timedelta(hours=hours)

    qs = SolarForecast.objects.filter(
        tenant=tenant,
        source=source,
        timestamp__gte=now,
        timestamp__lte=end,
    ).order_by("timestamp")

    total = qs.count()
    rows = list(qs[offset : offset + limit].values("timestamp", "forecast_kwh"))

    data = [
        {
            "timestamp": row["timestamp"],
            "value": float(row["forecast_kwh"]),
        }
        for row in rows
    ]

    return Response(
        {
            "tenant_id": str(tenant.id),
            "source": source,
            "unit": "kWh",
            "hours": hours,
            "limit": limit,
            "offset": offset,
            "total": total,
            "data": data,
        }
    )


# =========================================================
# FORECAST SOURCES
# GET /api/forecast/sources/?tenant=<uuid>
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def forecast_sources(request):
    tenant, error = _get_tenant_or_error(request)
    if error:
        return error

    sources = list(
        SolarForecast.objects.filter(tenant=tenant)
        .values_list("source", flat=True)
        .distinct()
    )

    return Response(
        {
            "tenant_id": str(tenant.id),
            "sources": sorted(sources),
        }
    )


# =========================================================
# FORECAST SUMMARY
# GET /api/forecast/summary/?tenant=<uuid>&hours=24
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def forecast_summary(request):
    tenant, error = _get_tenant_or_error(request)
    if error:
        return error

    hours = _parse_int(request.GET.get("hours"), 24)

    now = _ceil_to_next_hour(timezone.now())
    end = now + timedelta(hours=hours)

    rows = list(
        SolarForecast.objects.filter(
            tenant=tenant,
            timestamp__gte=now,
            timestamp__lte=end,
        ).order_by("timestamp")
    )

    result = {
        "tenant_id": str(tenant.id),
        "hours": hours,
        "counts": {
            "ml": 0,
            "physics": 0,
            "hybrid": 0,
        },
        "latest": {
            "ml": None,
            "physics": None,
            "hybrid": None,
        },
    }

    latest_per_source = {}

    for row in rows:
        if row.source in result["counts"]:
            result["counts"][row.source] += 1
            latest_per_source[row.source] = row

    for source, row in latest_per_source.items():
        result["latest"][source] = {
            "timestamp": row.timestamp,
            "value": float(row.forecast_kwh),
        }

    return Response(result)


# =========================================================
# FORECAST RECOMMENDATION
# GET /api/forecast/recommendation/?tenant=<uuid>&source=hybrid&hours=24&window_hours=3
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def forecast_recommendation(request):
    tenant, error = _get_tenant_or_error(request)
    if error:
        return error

    source = request.GET.get("source", "hybrid")
    hours = _parse_int(request.GET.get("hours"), 24)
    window_hours = _parse_int(request.GET.get("window_hours"), 3)

    if source not in VALID_SOURCES:
        return Response(
            {
                "error": f"invalid source '{source}'",
                "valid_sources": sorted(VALID_SOURCES),
            },
            status=400,
        )

    if window_hours < 1:
        return Response({"error": "window_hours must be >= 1"}, status=400)

    now = _ceil_to_next_hour(timezone.now())
    end = now + timedelta(hours=hours)

    rows = list(
        SolarForecast.objects.filter(
            tenant=tenant,
            source=source,
            timestamp__gte=now,
            timestamp__lte=end,
        )
        .order_by("timestamp")
        .values("timestamp", "forecast_kwh")
    )

    if not rows:
        return Response(
            {
                "tenant_id": str(tenant.id),
                "source": source,
                "hours": hours,
                "window_hours": window_hours,
                "best_hour": None,
                "best_window": None,
                "message": "no forecast data available",
            }
        )

    # Beste Stunde
    best_hour_row = max(rows, key=lambda r: float(r["forecast_kwh"]))
    best_hour = {
        "timestamp": best_hour_row["timestamp"],
        "value": float(best_hour_row["forecast_kwh"]),
    }

    # Bestes Zeitfenster
    best_window = None
    message = None

    if len(rows) < window_hours:
        message = "not enough data for window"
    else:
        best_sum = None

        for i in range(len(rows) - window_hours + 1):
            window = rows[i : i + window_hours]
            window_sum = sum(float(r["forecast_kwh"]) for r in window)

            if best_sum is None or window_sum > best_sum:
                best_sum = window_sum
                best_window = {
                    "start": window[0]["timestamp"],
                    "end": window[-1]["timestamp"],
                    "hours": window_hours,
                    "total_kwh": window_sum,
                    "avg_kwh": window_sum / window_hours,
                }

    result = {
        "tenant_id": str(tenant.id),
        "source": source,
        "hours": hours,
        "window_hours": window_hours,
        "best_hour": best_hour,
        "best_window": best_window,
    }

    if message:
        result["message"] = message

    return Response(result)


# =========================================================
# GLOBAL FORECAST (optional / staff only)
# GET /api/forecast/global/?source=hybrid&hours=24&limit=500&offset=0
# =========================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def global_forecast(request):
    if not request.user.is_staff:
        return Response({"error": "not allowed"}, status=403)

    source = request.GET.get("source")
    hours = _parse_int(request.GET.get("hours"), 24)
    limit = _parse_int(request.GET.get("limit"), 500)
    offset = _parse_int(request.GET.get("offset"), 0)

    if source and source not in VALID_SOURCES:
        return Response(
            {
                "error": f"invalid source '{source}'",
                "valid_sources": sorted(VALID_SOURCES),
            },
            status=400,
        )

    now = _ceil_to_next_hour(timezone.now())
    end = now + timedelta(hours=hours)

    qs = SolarForecast.objects.filter(
        timestamp__gte=now,
        timestamp__lte=end,
    ).order_by("timestamp")

    if source:
        qs = qs.filter(source=source)

    total = qs.count()
    rows = qs[offset : offset + limit]

    data = [
        {
            "tenant_id": str(row.tenant_id),
            "timestamp": row.timestamp,
            "value": float(row.forecast_kwh),
            "source": row.source,
        }
        for row in rows
    ]

    return Response(
        {
            "hours": hours,
            "limit": limit,
            "offset": offset,
            "total": total,
            "data": data,
        }
    )

# =========================================================
# GLOBAL FORECAST PV- String
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generator_string_forecast(request, string_id):

    source = request.GET.get(
        "source",
        "physics",
    )

    hours = int(
        request.GET.get(
            "hours",
            24,
        )
    )

    now = timezone.now().replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    if timezone.now().minute > 0:
        now += timedelta(hours=1)

    rows = SolarForecast.objects.filter(
        generator_string_id=string_id,
        source=source,
        timestamp__gte=now,
    ).order_by("timestamp")[:hours]

    return Response(
        {
            "generator_string": string_id,
            "source": source,
            "hours": hours,
            "points": [
                {
                    "t": int(row.timestamp.timestamp()),
                    "v": float(row.forecast_kwh),
                }
                for row in rows
            ],
        }
    )


# =========================================================
# 🏠 HOME SOLAR FORECAST (Gesamtanlage / Strings)
# GET /api/forecast/home/?home_id=<uuid>&string_id=<uuid>&source=hybrid&hours=24
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def home_solar_forecast(request):
    home_id = request.GET.get("home_id")
    string_id = request.GET.get("string_id")
    source = request.GET.get("source", "hybrid")
    hours = int(request.GET.get("hours", 24))

    user_homes = request.user.homes.all()
    if not user_homes.exists():
        if request.user.is_staff:
            home = Home.objects.first()
        else:
            return Response({"error": "No home configured"}, status=404)
    else:
        if home_id:
            home = user_homes.filter(id=home_id).first() or user_homes.first()
        else:
            home = user_homes.first()

    if not home:
        return Response({"error": "Home not found"}, status=404)

    strings = list(
        GeneratorString.objects.filter(generator__home=home)
        .select_related("generator", "orientation")
    )

    if not strings:
        strings = list(GeneratorString.objects.all().select_related("generator", "orientation"))

    if string_id and string_id != "all":
        target_strings = [s for s in strings if str(s.id) == str(string_id)]
    else:
        target_strings = strings

    now = timezone.now().replace(minute=0, second=0, microsecond=0)
    if timezone.now().minute > 0:
        now += timedelta(hours=1)

    target_string_ids = [s.id for s in target_strings]

    qs = SolarForecast.objects.filter(
        generator_string_id__in=target_string_ids,
        source=source,
        timestamp__gte=now,
    ).order_by("timestamp")

    if not qs.exists() and source == "hybrid":
        qs = SolarForecast.objects.filter(
            generator_string_id__in=target_string_ids,
            source="physics",
            timestamp__gte=now,
        ).order_by("timestamp")
        source = "physics"

    points_by_ts = defaultdict(float)
    for row in qs:
        points_by_ts[row.timestamp] += float(row.forecast_kwh or 0)

    sorted_ts = sorted(points_by_ts.keys())[:hours]
    points = [
        {
            "t": int(ts.timestamp()),
            "v": round(points_by_ts[ts], 3),
        }
        for ts in sorted_ts
    ]

    total_kwh = sum(p["v"] for p in points)
    peak_point = max(points, key=lambda p: p["v"]) if points else None

    return Response({
        "home_id": str(home.id),
        "home_name": home.name,
        "source": source,
        "hours": hours,
        "strings": [
            {
                "id": str(s.id),
                "name": s.name,
                "peak_power_kwp": float(s.peak_power_kwp or 0),
                "orientation": s.orientation.name if s.orientation else "Süd",
            }
            for s in strings
        ],
        "selected_string_id": string_id or "all",
        "total_kwh": round(total_kwh, 2),
        "peak_kwh": peak_point["v"] if peak_point else 0.0,
        "peak_time": peak_point["t"] if peak_point else None,
        "points": points,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def household_load_forecast(request):
    from forecast.services_load_forecast import get_household_load_forecast
    horizon = _parse_int(request.GET.get("horizon"), 48)
    data = get_household_load_forecast(request.user, horizon_hours=horizon)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def solar_forecast_accuracy_view(request):
    from forecast.services_accuracy import get_solar_forecast_accuracy
    period = request.GET.get("period", "today")
    string_id = request.GET.get("string_id", "all")
    data = get_solar_forecast_accuracy(request.user, period=period, string_id=string_id)
    return Response(data)

