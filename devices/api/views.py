######################
# devices/api/views.py
######################

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery, Q
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

    metric_map = {}

    for d in devices:
        config = getattr(d, "config", None)

        if config and config.metric_definition:
            metric_map[d.id] = config.metric_definition.key

    sparkline_rows = (
        DeviceMetric1m.objects.filter(
            device_id__in=device_ids,
            bucket__gte=since,
        )
        .values(
            "device_id",
            "metric_key",
            "avg",
        )
        .order_by(
            "device_id",
            "bucket",
        )
    )

    sparkline_map = defaultdict(list)

    for row in sparkline_rows:
        expected_key = metric_map.get(row["device_id"])
        if expected_key and row["metric_key"] != expected_key:
            continue

        sparkline_map[row["device_id"]].append(
            round(
                float(row["avg"] or 0),
                2,
            )
        )

    # Fallback auf DeviceMetric, falls DeviceMetric1m für ein Gerät noch leer ist
    missing_sparkline_devs = [d.id for d in devices if not sparkline_map.get(d.id)]
    if missing_sparkline_devs:
        raw_rows = (
            DeviceMetric.objects.filter(
                device_id__in=missing_sparkline_devs,
                timestamp__gte=since,
                metric_key__in=["power", "value"],
            )
            .values("device_id", "value")
            .order_by("device_id", "timestamp")[:300]
        )
        for r in raw_rows:
            if r["value"] is not None:
                sparkline_map[r["device_id"]].append(round(float(r["value"]), 2))

    result = []

    for d in devices:

        config = getattr(d, "config", None)

        metric = (
            config.metric_definition if config and config.metric_definition else None
        )

        result.append(
            {
                "device": d.id,
                "value": values.get(d.id),
                "unit": metric.unit if metric else "",
                "sparkline": sparkline_map.get(d.id, []),
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
def device_timeseries(request, device_id):
    range_str = request.GET.get("range", "24h")

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

    qs = list(
        config["model"]
        .objects.filter(device_id=device_id)
        .filter(Q(metric_key__in=possible_keys) | Q(metric_key__isnull=True))
        .filter(**{f"{field}__gte": start, f"{field}__lte": now})
        .order_by(field)
    )

    value_field = config["value_field"]

    if not qs and config.get("fallback_model"):
        fb_model = config["fallback_model"]
        fb_field = config["fallback_field"]
        qs = list(
            fb_model.objects.filter(device_id=device_id)
            .filter(Q(metric_key__in=possible_keys) | Q(metric_key__isnull=True))
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

    return Response(
        {
            "device": device_id,
            "range": range_str,
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
