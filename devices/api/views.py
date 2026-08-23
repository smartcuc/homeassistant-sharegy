######################
# devices/api/views.py
######################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery, Q
from datetime import timedelta
from django.utils import timezone

from devices.models import (
    Device,
    DeviceConfig,
    DeviceRole,
    Room,
    Floor,
    Home,
    MQTTProfile,
    MetricDefinition,
    DeviceMetric,
    DeviceLatestMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
)

from producer.models import GeneratorSystem, GeneratorType
from energy.models import EMSSignalType

from devices.services.metrics import get_latest_values
from .serializers import (
    DeviceSerializer,
    DeviceConfigSerializer,
    HomeSerializer,
    DeviceRoleSerializer,
    MQTTProfileSerializer,
)

from collections import defaultdict

# ============================================================
# ✅ SETUP OPTIONS
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_setup_options(request):

    roles = DeviceRole.objects.all()
    rooms = Room.objects.all()
    floors = Floor.objects.all()
    metrics = MetricDefinition.objects.all()

    generator_types = GeneratorType.objects.filter(active=True)

    return Response(
        {
            "roles": DeviceRoleSerializer(
                roles,
                many=True,
            ).data,
            "rooms": [{"id": r.id, "name": r.name} for r in rooms],
            "floors": [{"id": f.id, "name": f.name} for f in floors],
            "metric_definitions": [
                {
                    "id": m.id,
                    "key": m.key,
                    "name": m.name,
                    "unit": m.unit,
                }
                for m in metrics
            ],
            "generator_types": [
                {
                    "id": g.id,
                    "key": g.key,
                    "name": g.name,
                    "icon": g.icon,
                }
                for g in generator_types
            ],
            "energy_signal_types": [
                {
                    "id": s.id,
                    "key": s.key,
                    "name": s.label,
                }
                for s in EMSSignalType.objects.filter(active=True).order_by("label")
            ],
        }
    )


# ============================================================
# ✅ ALL DEVICES
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_list(request):

    devices = Device.objects.filter(
        home__user=request.user,
        active=True,
        pending_delete=False,
    ).select_related(
        "config",
        "config__role",
        "config__room",
        "config__floor",
    )
    return Response(DeviceSerializer(devices, many=True).data)


# ============================================================
# ✅ UNCONFIGURED (für Modal)
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unconfigured_devices(request):

    devices = Device.objects.filter(
        home__user=request.user,
        active=True,
        pending_delete=False,
    ).select_related(
        "config",
        "config__role",
        "config__room",
        "config__floor",
    )

    result = []

    for d in devices:
        config = getattr(d, "config", None)

        if not config or not config.is_classified():
            result.append(DeviceSerializer(d).data)

    return Response({"devices": result})


# ============================================================
# ✅ CONFIGURE DEVICE
# ============================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def configure_device(request, device_id):

    user = request.user

    device = get_object_or_404(Device, id=device_id, home__user=user)

    config, _ = DeviceConfig.objects.get_or_create(
        device=device,
        defaults={"home": device.home}
    )

    serializer = DeviceConfigSerializer(
        config,
        data=request.data,
        partial=True,
        context={"request": request},
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    # ✅ ✅ ✅ HIER IST DER FIX
    config.refresh_from_db()

    #
    # Producer automatisch anlegen
    #
    if (
        config.role
        and config.role.key == "producer"
        and config.generator_type
    ):

        GeneratorSystem.objects.get_or_create(
            device=device,
            defaults={
                "home": device.home,
                "name": config.display_name(),
                "generator_type":
                    config.generator_type,
            },
        )

    device.configured = config.is_classified()
    device.save(update_fields=["configured"])

    return Response({
        "status": "ok",
        "device": DeviceSerializer(device).data
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sankey_data(request):

    user = request.user

    devices = list(
        Device.objects
        .filter(home__user=user)
        .select_related("config__role")
    )

    latest_power_map = get_latest_values([d.id for d in devices])
    for d in devices:
        d.latest_power = latest_power_map.get(d.id, 0.0)

    nodes = []
    links = []
    added = set()

    def nid(d):
        return f"device_{d.id}"

    def label(d):
        if d.config:
            return d.config.display_name()
        return d.identifier

    def add_node(i, l):
        if i not in added:
            nodes.append({"id": i, "label": l})
            added.add(i)

    def add_link(s, t, v):
        if v and v > 0:
            links.append({
                "source": s,
                "target": t,
                "value": round(v, 2)
            })

    HOUSE = "house"
    add_node(HOUSE, "Haus")

    producers, consumers, storages = [], [], []

    for d in devices:
        config = getattr(d, "config", None)
        if not config or not config.is_classified():
            continue

        role = config.role
        if not role:
            continue

        power = d.latest_power or 0

        if role.key == "producer":
            producers.append((d, power))
        elif role.key == "consumer":
            consumers.append((d, power))
        elif role.key == "both":
            storages.append((d, power))

    for d, _ in producers + consumers + storages:
        add_node(nid(d), label(d))

    total_prod = sum(p for _, p in producers if p > 0)

    for d, p in producers:
        add_link(nid(d), HOUSE, p)

    for d, p in storages:
        if p > 0:
            add_link(nid(d), HOUSE, p)
        elif p < 0:
            charge = abs(p)

            for pd, pp in producers:
                if total_prod > 0 and pp > 0:
                    share = pp / total_prod
                    add_link(nid(pd), nid(d), charge * share)

    for d, p in consumers:
        add_link(HOUSE, nid(d), p)

    return Response({
        "nodes": nodes,
        "links": links
    })


# ============================================================
# ✅ LATEST DEVCE VALUE
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_device_values(request):

    devices = list(
        Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        ).select_related("config")
    )

    values = get_latest_values([d.id for d in devices])

    result = []

    for d in devices:

        value = values.get(d.id)

        if value is None:
            continue

        config = getattr(d, "config", None)

        metric = (
            config.metric_definition
            if config and config.metric_definition
            else None
        )

        result.append(
            {
                "device": d.id,
                "value": value,
                "unit": metric.unit if metric else "",
            }
        )

    return Response(result)

# ============================================================
# ✅ DEVICE DASHBOARD VALUES
# ============================================================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_dashboard_values(request):

    devices = list(
        Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        ).select_related(
            "config",
            "config__metric_definition",
        )
    )

    device_ids = [d.id for d in devices]

    values = get_latest_values(device_ids)

    since = timezone.now() - timedelta(hours=1)

    # 1. Sammle 1m Aggregationen der letzten Stunde
    sparkline_rows = list(
        DeviceMetric1m.objects.filter(
            device_id__in=device_ids,
            bucket__gte=since,
        )
        .filter(Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True))
        .values("device_id", "avg")
        .order_by("device_id", "bucket")
    )

    sparkline_map = defaultdict(list)
    for row in sparkline_rows:
        sparkline_map[row["device_id"]].append(
            round(float(row["avg"] or 0), 2)
        )

    # 2. Resilienter Fallback für Geräte mit wenigen / keinen Punkten in der letzten Stunde
    for d in devices:
        pts = sparkline_map.get(d.id, [])
        if len(pts) < 3:
            # Versuche jüngste 30 Punkte aus DeviceMetric1m
            recent_1m = list(
                DeviceMetric1m.objects.filter(device_id=d.id)
                .filter(Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True))
                .order_by("-bucket")
                .values_list("avg", flat=True)[:30]
            )
            if len(recent_1m) >= 2:
                sparkline_map[d.id] = [round(float(v or 0), 2) for v in reversed(recent_1m)]
            else:
                # Versuche jüngste 30 Punkte aus Rohdaten (DeviceMetric)
                recent_raw = list(
                    DeviceMetric.objects.filter(device_id=d.id)
                    .filter(Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True))
                    .order_by("-timestamp")
                    .values_list("value", flat=True)[:30]
                )
                if recent_raw:
                    sparkline_map[d.id] = [
                        round(float(v), 2) for v in reversed(recent_raw) if v is not None
                    ]

    result = []

    for d in devices:
        config = getattr(d, "config", None)
        metric = (
            config.metric_definition if config and config.metric_definition else None
        )

        sparkline_pts = sparkline_map.get(d.id, [])
        if len(sparkline_pts) == 1:
            sparkline_pts = [sparkline_pts[0], sparkline_pts[0]]

        result.append(
            {
                "device": d.id,
                "value": values.get(d.id),
                "unit": metric.unit if metric else "",
                "sparkline": sparkline_pts,
            }
        )

    return Response(result)


# ============================================================
# ✅ TIMESERIES API
# ============================================================

def get_range_config(range_str):
    if range_str == "1h":
        return {
            "model": DeviceMetric1m,
            "fallback_model": DeviceMetric,
            "delta": timedelta(hours=1),
            "field": "bucket",
            "fallback_field": "timestamp",
            "value_field": "avg",
            "fallback_value_field": "value",
        }

    if range_str == "6h":
        return {
            "model": DeviceMetric5m,
            "fallback_model": DeviceMetric1m,
            "delta": timedelta(hours=6),
            "field": "bucket",
            "fallback_field": "bucket",
            "value_field": "avg",
            "fallback_value_field": "avg",
        }

    if range_str == "24h":
        return {
            "model": DeviceMetric15m,
            "fallback_model": DeviceMetric5m,
            "delta": timedelta(hours=24),
            "field": "bucket",
            "fallback_field": "bucket",
            "value_field": "avg",
            "fallback_value_field": "avg",
        }

    if range_str == "5d":
        return {
            "model": DeviceMetric1h,
            "fallback_model": DeviceMetric15m,
            "delta": timedelta(days=5),
            "field": "bucket",
            "fallback_field": "bucket",
            "value_field": "avg",
            "fallback_value_field": "avg",
        }

    raise ValueError("invalid_range")


@api_view(["GET"])
def device_available_metrics(request, device_id):
    """
    Liefert alle aktiven Messwert-Kanäle eines Geräts (für Multi-Metric Devices).
    """
    device = get_object_or_404(
        Device.objects.select_related("config__metric_definition"),
        id=device_id,
    )

    primary_key = (
        device.config.metric_definition.key
        if hasattr(device, "config") and device.config and device.config.metric_definition
        else "power"
    )

    latest_metrics = DeviceLatestMetric.objects.filter(device_id=device_id).order_by("metric_key")

    KEY_METADATA = {
        "power": {"name": "Wirkleistung", "unit": "W", "icon": "⚡"},
        "active_power": {"name": "Wirkleistung", "unit": "W", "icon": "⚡"},
        "p_total": {"name": "Gesamtleistung", "unit": "W", "icon": "⚡"},
        "value": {"name": "Leistung", "unit": "W", "icon": "⚡"},
        "voltage": {"name": "Spannung", "unit": "V", "icon": "🔌"},
        "voltage_l1": {"name": "Spannung L1", "unit": "V", "icon": "🔌"},
        "voltage_l2": {"name": "Spannung L2", "unit": "V", "icon": "🔌"},
        "voltage_l3": {"name": "Spannung L3", "unit": "V", "icon": "🔌"},
        "current": {"name": "Strom", "unit": "A", "icon": "⚡"},
        "current_l1": {"name": "Strom L1", "unit": "A", "icon": "⚡"},
        "current_l2": {"name": "Strom L2", "unit": "A", "icon": "⚡"},
        "current_l3": {"name": "Strom L3", "unit": "A", "icon": "⚡"},
        "soc": {"name": "Batterieladestand", "unit": "%", "icon": "🔋"},
        "battery_soc": {"name": "Batterieladestand", "unit": "%", "icon": "🔋"},
        "energy": {"name": "Energie", "unit": "kWh", "icon": "📊"},
        "energy_import": {"name": "Netzbezug", "unit": "kWh", "icon": "📥"},
        "energy_export": {"name": "Einspeisung", "unit": "kWh", "icon": "📤"},
        "frequency": {"name": "Frequenz", "unit": "Hz", "icon": "〰️"},
        "temperature": {"name": "Temperatur", "unit": "°C", "icon": "🌡️"},
    }

    def_map = {d.key: d for d in MetricDefinition.objects.all()}

    results = []
    seen_keys = set()

    for lm in latest_metrics:
        k = lm.metric_key
        if k.startswith("state."):
            continue
        seen_keys.add(k)
        meta = KEY_METADATA.get(k, {})
        d_obj = def_map.get(k)

        name = d_obj.name if d_obj else meta.get("name", k.replace("_", " ").title())
        unit = lm.unit or (d_obj.unit if d_obj else meta.get("unit", ""))
        icon = meta.get("icon", "📈")

        is_primary = (k == primary_key) or (primary_key not in seen_keys and k in ["power", "value", "active_power"])

        results.append({
            "key": k,
            "name": name,
            "unit": unit,
            "icon": icon,
            "latest_value": lm.value,
            "timestamp": lm.timestamp.isoformat() if lm.timestamp else None,
            "is_primary": is_primary,
        })

    if not results:
        results.append({
            "key": primary_key,
            "name": "Leistung",
            "unit": "W",
            "icon": "⚡",
            "latest_value": None,
            "timestamp": None,
            "is_primary": True,
        })

    return Response({"metrics": results, "primary_metric": primary_key})


@api_view(["GET"])
def device_timeseries(request, device_id):
    range_str = request.GET.get("range", "24h")
    requested_metric = request.GET.get("metric")

    try:
        config = get_range_config(range_str)
    except ValueError:
        return Response(
            {"error": "invalid_range"},
            status=400,
        )

    device = get_object_or_404(
        Device.objects.select_related("config__metric_definition"),
        id=device_id,
    )

    if requested_metric:
        possible_keys = [requested_metric]
    else:
        possible_keys = ["power", "value"]
        if hasattr(device, "config") and device.config and device.config.metric_definition:
            possible_keys.append(device.config.metric_definition.key)

    now = timezone.now()
    field = config["field"]

    if field == "bucket":
        now = now.replace(
            second=0,
            microsecond=0,
        )

    start = now - config["delta"]

    metric_filter = Q(metric_key__in=possible_keys)
    if not requested_metric:
        metric_filter |= Q(metric_key__isnull=True)

    qs = list(
        config["model"]
        .objects.filter(device_id=device_id)
        .filter(metric_filter)
        .filter(**{f"{field}__gte": start, f"{field}__lte": now})
        .order_by(field)
    )

    value_field = config["value_field"]

    if not qs and config.get("fallback_model"):
        fb_model = config["fallback_model"]
        fb_field = config["fallback_field"]
        qs = list(
            fb_model.objects.filter(device_id=device_id)
            .filter(metric_filter)
            .filter(**{f"{fb_field}__gte": start, f"{fb_field}__lte": now})
            .order_by(fb_field)
        )
        field = fb_field
        value_field = config.get("fallback_value_field", "avg")

    points = []
    for row in qs:
        t = getattr(row, field).timestamp()
        v = getattr(row, value_field)
        points.append(
            {
                "t": int(t),
                "v": round(float(v), 2) if v is not None else 0.0,
                "min": getattr(row, "min", None),
                "max": getattr(row, "max", None),
            }
        )

    unit = "W"
    effective_metric = requested_metric or possible_keys[0]
    latest_m = DeviceLatestMetric.objects.filter(device_id=device_id, metric_key=effective_metric).first()
    if latest_m and latest_m.unit:
        unit = latest_m.unit
    else:
        def_obj = MetricDefinition.objects.filter(key=effective_metric).first()
        if def_obj and def_obj.unit:
            unit = def_obj.unit

    return Response(
        {
            "device": device_id,
            "range": range_str,
            "metric": effective_metric,
            "unit": unit,
            "points": points,
        }
    )



@api_view(["GET"])
def list_homes(request):
    homes = Home.objects.filter(user=request.user)
    serializer = HomeSerializer(homes, many=True)
    return Response(serializer.data)

# ============================================================
# ✅ REMOVE DEVICES
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_devices(request):


    updated = Device.objects.filter(
        active=False,
        pending_delete=True,
        delete_after=delete_after,
    )
    return Response({
        "updated": updated,
        "delete_after": delete_after,
    })


# ============================================================
# ✅ RESTORE DEVICES
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def restore_devices(request):

    device_ids = request.data.get("device_ids", [])

    updated = Device.objects.filter(
        id__in=device_ids,
        home__user=request.user,
        pending_delete=True,
    ).update(
        active=True,
        pending_delete=False,
        delete_after=None,
    )

    return Response({
        "updated": updated,
    })


# ============================================================
# ✅ TRASH BIN
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trash_devices(request):

    devices = Device.objects.filter(
        home__user=request.user,
        pending_delete=True,
    )

    return Response(
        DeviceSerializer(devices, many=True).data
    )


# ============================================================
# ✅ PURGE DEVICES
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def purge_devices(request):

    device_ids = request.data.get("device_ids", [])

    deleted, _ = Device.objects.filter(
        id__in=device_ids,
        home__user=request.user,
        pending_delete=True,
    ).delete()

    return Response({
        "deleted": deleted,
    })


# ============================================================
# ✅ TRASH COUNT
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trash_count(request):

    count = Device.objects.filter(
        home__user=request.user,
        pending_delete=True,
    ).count()

    return Response({
        "count": count,
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mqtt_profile_list(request):

    profiles = MQTTProfile.objects.filter(
        active=True
    ).order_by("name")

    return Response(
        MQTTProfileSerializer(
            profiles,
            many=True,
        ).data
    )
