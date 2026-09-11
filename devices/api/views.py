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

import os
from devices.services.metrics import get_latest_values
from devices.serializers import DeviceCreateSerializer
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

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def device_list(request):
    if request.method == "POST":
        serializer = DeviceCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        device = serializer.save()

        return Response({
            "id": device.id,
            "identifier": device.identifier,
            "mqtt_token": device.home.mqtt_token,
            "mqtt_username": device.home.mqtt_username,
            "mqtt_password": device.home.mqtt_password,
            "mqtt_host": os.getenv("MQTT_HOST"),
            "mqtt_port": int(os.getenv("MQTT_PORT", 1883)),
        }, status=201)

    devices = Device.objects.filter(
        home__user=request.user,
        active=True,
        pending_delete=False,
    ).select_related(
        "config",
        "config__role",
        "config__metric_definition",
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
        "config__metric_definition",
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

    # ✅ Snapshot-Bereinigung & Aktualisierung ohne UniqueConstraint-Konflikt
    if config.metric_definition:
        new_key = config.metric_definition.key
        new_unit = config.metric_definition.unit
        try:
            target_snapshot = DeviceLatestMetric.objects.filter(device=device, metric_key=new_key).first()
            other_snapshots = list(
                DeviceLatestMetric.objects.filter(
                    device=device,
                    metric_key__in=["value", "val", "power", "temperature", "temp", "bwwp_temp"]
                ).exclude(metric_key=new_key)
            )

            if target_snapshot:
                target_snapshot.unit = new_unit
                target_snapshot.save(update_fields=["unit"])
                # Lösche überflüssige generische Alt-Snapshots
                for s in other_snapshots:
                    s.delete()
            elif other_snapshots:
                # Nutze den ersten bestehenden Snapshot und benenne ihn um
                primary_snap = other_snapshots[0]
                primary_snap.metric_key = new_key
                primary_snap.unit = new_unit
                primary_snap.save(update_fields=["metric_key", "unit"])
                # Alle weiteren Duplikate sicher löschen
                for s in other_snapshots[1:]:
                    s.delete()
        except Exception as e:
            logger.warning("[configure_device] Snapshot consolidation notice: %s", e)

    #
    # Producer automatisch anlegen
    #
    try:
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
                    "generator_type": config.generator_type,
                },
            )
    except Exception as e:
        logger.warning("[configure_device] GeneratorSystem auto-create notice: %s", e)

    #
    # Batteriespeicher (StorageSystem) automatisch anlegen
    #
    try:
        if (
            config.role
            and config.role.key in ["battery", "storage", "akku"]
        ) or (
            config.energy_signal_type
            and config.energy_signal_type.key in ["battery", "battery_storage"]
        ):
            from producer.models import StorageSystem
            from django.db.models import Q

            existing_storage = StorageSystem.objects.filter(
                home=device.home
            ).filter(
                Q(primary_device=device) | Q(soc_device=device) | Q(power_device=device)
            ).first()

            if not existing_storage:
                dev_name = config.display_name() if config.display_name() else device.identifier
                storage_name = dev_name if any(w in dev_name.lower() for w in ["speicher", "battery", "akku", "storage"]) else f"{dev_name} (Speicher)"

                capacity_kwh = 10.0
                if hasattr(device, "resource") and device.resource and device.resource.attributes:
                    cap = device.resource.attributes.get("capacity_kwh") or device.resource.attributes.get("battery_capacity_kwh")
                    if cap:
                        try:
                            capacity_kwh = float(cap)
                        except (ValueError, TypeError):
                            pass

                StorageSystem.objects.create(
                    home=device.home,
                    name=storage_name,
                    capacity_kwh=capacity_kwh,
                    primary_device=device,
                    soc_device=device,
                    soc_metric_key="soc",
                    power_device=device,
                    power_metric_key="power",
                    is_auto_detected=True,
                    active=True,
                )
    except Exception as e:
        logger.warning("[configure_device] StorageSystem auto-create notice: %s", e)

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


from django.core.cache import cache

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_dashboard_values(request):
    user = request.user
    # Opportunistisches Cloud-Polling: Falls Inverter-Integrationen aktiv sind, im Hintergrund auffrischen
    try:
        from devices.models import CloudDeviceIntegration
        from devices.services_profile_runner import execute_cloud_poll
        for integration in CloudDeviceIntegration.objects.filter(device__home__user=user, is_active=True):
            if not integration.last_polled_at or (timezone.now() - integration.last_polled_at).total_seconds() > 45:
                c_key = f"cloud_poll_lock_{integration.id}"
                if not cache.get(c_key):
                    cache.set(c_key, True, timeout=30)
                    try:
                        execute_cloud_poll(integration)
                    except Exception as poll_err:
                        logger.warning("Opportunistischer Cloud-Poll fehlgeschlagen: %s", poll_err)
    except Exception as e:
        logger.debug("Cloud poll trigger failed: %s", e)

    devices = list(
        Device.objects.filter(
            home__user=request.user,
            active=True,
            pending_delete=False,
        ).select_related(
            "config",
            "config__role",
            "config__metric_definition",
            "config__energy_signal_type",
        )
    )

    device_ids = [d.id for d in devices]

    values = get_latest_values(device_ids)
    from devices.services.ingest import _infer_canonical_unit

    device_cfg_map = {d.id: getattr(d, "config", None) for d in devices}

    all_latest = list(
        DeviceLatestMetric.objects.filter(device_id__in=device_ids).values(
            "device_id", "metric_key", "value", "unit", "timestamp"
        )
    )
    # Erkennung von Multi-Source-Invertern je Gerät
    dev_keys_map = defaultdict(set)
    for row in all_latest:
        dev_keys_map[row["device_id"]].add(row["metric_key"].lower())

    device_metrics_map = defaultdict(dict)
    for row in all_latest:
        dev_id = row["device_id"]
        cfg = device_cfg_map.get(dev_id)
        configured_lead_key = cfg.metric_definition.key if (cfg and cfg.metric_definition) else None
        m_k = row["metric_key"]
        raw_keys = dev_keys_map[dev_id]
        is_multi_source = any(k in raw_keys for k in ["pv_power", "grid_power", "battery_power", "load_power"])

        # 1. soc -> battery_soc
        if m_k.lower() in ["soc", "battery_level"]:
            m_k = "battery_soc"

        # 2. Generische Keys (value, val) auf konfigurierte Lead-Metrik mappen
        if m_k.lower() in ["value", "val"] and configured_lead_key:
            m_k = configured_lead_key

        # 3. Single-Channel Submeter / Verbraucher: generische 'power'/'temperature' mit konfigurierter Lead-Metrik zusammenführen
        if not is_multi_source and configured_lead_key:
            cfg_lower = configured_lead_key.lower()
            k_lower = m_k.lower()
            if ("power" in cfg_lower or cfg_lower in ["aircon_power", "heatpump_power", "bwwp_power", "wallbox_power"]) and k_lower in ["power", "active_power", "p_total", "w", "watt", "value", "val"]:
                m_k = configured_lead_key
            elif "temp" in cfg_lower and k_lower in ["temperature", "temp", "device_temp", "value", "val"]:
                m_k = configured_lead_key

        inferred_u = _infer_canonical_unit(m_k, row["unit"] or "", config=cfg)
        val = round(float(row["value"]), 2) if row["value"] is not None else None
        cached_val = cache.get(f"device:{dev_id}:{m_k}") or cache.get(f"device:{dev_id}:{row['metric_key']}")
        if cached_val is not None:
            try:
                val = round(float(cached_val), 2)
            except (ValueError, TypeError):
                pass

        device_metrics_map[dev_id][m_k] = {
            "value": val,
            "unit": inferred_u,
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
        }

    since = timezone.now() - timedelta(hours=1)
    POWER_KEYS = {"power", "value", "val", "apower", "active_power", "pv_power", "load_power", "grid_power", "battery_power"}

    # 1. 1m Sparkline-Rollups laden
    all_1m_rows = list(
        DeviceMetric1m.objects.filter(
            device_id__in=device_ids,
            bucket__gte=since,
        )
        .values("device_id", "metric_key", "avg", "bucket")
        .order_by("device_id", "bucket")
    )

    sparkline_1m_by_device = defaultdict(lambda: defaultdict(list))
    for row in all_1m_rows:
        if row["avg"] is not None:
            m_k = (row["metric_key"] or "").lower()
            sparkline_1m_by_device[row["device_id"]][m_k].append(round(float(row["avg"]), 2))

    # 2. Die absolut echten, jüngsten Live-Messwerte aus DeviceMetric laden (exakt dieselbe Quelle wie DeviceChartModal)
    recent_raw_rows = list(
        DeviceMetric.objects.filter(
            device_id__in=device_ids,
            timestamp__gte=since,
        )
        .values("device_id", "metric_key", "value", "unit", "timestamp")
        .order_by("device_id", "timestamp")
    )

    for row in recent_raw_rows:
        dev_id = row["device_id"]
        raw_k = (row["metric_key"] or "").lower()
        cfg = device_cfg_map.get(dev_id)

        if row["value"] is not None:
            val = round(float(row["value"]), 2)
            sparkline_1m_by_device[dev_id][raw_k].append(val)
            inferred_u = _infer_canonical_unit(raw_k, row["unit"] or "", config=cfg)
            if dev_id not in device_metrics_map:
                device_metrics_map[dev_id] = {}
            device_metrics_map[dev_id][raw_k] = {
                "value": val,
                "unit": inferred_u,
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
            }

    result = []

    for d in devices:
        config = getattr(d, "config", None)
        metric = (
            config.metric_definition if config and config.metric_definition else None
        )
        role_key = (config.role.key if config and config.role else "").lower()
        sig_key = (config.energy_signal_type.key if config and config.energy_signal_type else "").lower()
        is_grid = getattr(config, "is_grid_source", False) or role_key in ["grid", "meter", "smart_meter", "zaehler"] or sig_key in ["grid", "meter", "grid_import", "grid_feed_in"]
        configured_lead = metric.key if metric else None

        dev_metrics = device_metrics_map.get(d.id, {})

        # Kandidaten-Reihenfolge zur präzisen Bestimmung des Haupt-Messwerts:
        candidate_keys = []
        is_generic_lead = not configured_lead or configured_lead.lower() in ["power", "value", "val", "main"]

        if not is_generic_lead:
            candidate_keys.append(configured_lead)

        if is_grid:
            candidate_keys.extend(["grid_power", "power_grid", "active_power", "p_total", "power"])
        elif role_key in ["producer", "pv", "solar"] or sig_key in ["pv", "solar", "producer"]:
            candidate_keys.extend(["pv_power", "solar_power", "yield_power", "power"])
        elif role_key in ["both", "hybrid", "inverter", "storage_inverter"] or sig_key in ["both", "hybrid"]:
            candidate_keys.extend(["pv_power", "solar_power", "yield_power", "power", "battery_soc", "battery_power", "load_power", "grid_power"])
        elif role_key in ["battery", "storage"] or sig_key in ["battery", "storage"]:
            candidate_keys.extend(["battery_soc", "soc", "battery_power", "power"])
        elif role_key in ["consumer", "load"] or sig_key in ["load", "consumer"]:
            candidate_keys.extend(["load_power", "aircon_power", "heatpump_power", "bwwp_power", "wallbox_power", "power", "active_power"])
        elif role_key == "sensor":
            candidate_keys.extend(["temperature", "temp", "humidity", "pressure", "value"])
        else:
            candidate_keys.extend(["pv_power", "solar_power", "yield_power", "power", "battery_soc", "battery_power", "load_power", "grid_power", "value", "val"])

        if configured_lead and configured_lead not in candidate_keys:
            candidate_keys.append(configured_lead)

        # Sparkline-Punkte blitzschnell aus dem In-Memory Mapping extrahieren
        is_pwr = (configured_lead or "").lower() in POWER_KEYS or is_grid or role_key in ["producer", "consumer", "grid", "both", "hybrid", ""]
        dev_sparklines = sparkline_1m_by_device.get(d.id, {})
        sparkline_pts = []
        matched_key = None

        if is_pwr:
            for p_k in candidate_keys + list(POWER_KEYS):
                if p_k.lower() in dev_sparklines and dev_sparklines[p_k.lower()]:
                    sparkline_pts = dev_sparklines[p_k.lower()]
                    matched_key = p_k.lower()
                    break
            if not sparkline_pts and "" in dev_sparklines:
                sparkline_pts = dev_sparklines[""]
        else:
            # Spezifische oder Alias-Metrik suchen
            alias_keys = [c.lower() for c in candidate_keys]
            if "temp" in (configured_lead or "").lower():
                alias_keys.extend(["temperature", "temp", "device_temp", "bwwp_temp", "water_temp", "sensor_temp", "value", "val"])
            elif "soc" in (configured_lead or "").lower():
                alias_keys.extend(["soc", "battery_soc", "battery_level", "value", "val"])
            elif "volt" in (configured_lead or "").lower():
                alias_keys.extend(["voltage", "voltage_l1", "value", "val"])
            elif "curr" in (configured_lead or "").lower():
                alias_keys.extend(["current", "current_l1", "value", "val"])
            else:
                alias_keys.extend(["value", "val"])

            for a_k in alias_keys:
                if a_k in dev_sparklines and dev_sparklines[a_k]:
                    sparkline_pts = dev_sparklines[a_k]
                    matched_key = a_k
                    break

        # Fallback falls keine aggregierten Punkte vorhanden
        if not sparkline_pts and dev_sparklines:
            first_key, first_pts = next(iter(dev_sparklines.items()), (None, []))
            if first_pts:
                sparkline_pts = first_pts
                matched_key = first_key

        lead_val = None
        top_unit = _infer_canonical_unit(matched_key or configured_lead or "power", metric.unit if metric else "", config=config)

        # 1. Höchste Priorität: Match über Candidate Keys in dev_metrics / Redis-Live-Cache
        for c_k in candidate_keys:
            cached_v = cache.get(f"device:{d.id}:{c_k}")
            if cached_v is not None:
                try:
                    lead_val = round(float(cached_v), 2)
                    top_unit = dev_metrics.get(c_k, {}).get("unit") or top_unit
                    break
                except (ValueError, TypeError):
                    pass
            if c_k in dev_metrics and dev_metrics[c_k]["value"] is not None:
                lead_val = dev_metrics[c_k]["value"]
                top_unit = dev_metrics[c_k]["unit"] or top_unit
                break

        # 2. Fallback auf jüngsten Sparkline-Punkt
        if lead_val is None and sparkline_pts:
            lead_val = sparkline_pts[-1]

        # 3. Fallback auf get_latest_values
        if lead_val is None and values.get(d.id) is not None:
            lead_val = values.get(d.id)

        # 4. Fallback auf erste verfügbare Metrik
        if lead_val is None and dev_metrics:
            first_m = next((m for m in dev_metrics.values() if m.get("value") is not None), None)
            if first_m:
                lead_val = first_m.get("value")
                top_unit = first_m.get("unit") or top_unit

        if len(sparkline_pts) == 1:
            sparkline_pts = [sparkline_pts[0], sparkline_pts[0]]
        elif not sparkline_pts and lead_val is not None:
            sparkline_pts = [lead_val, lead_val]

        result.append(
            {
                "device": d.id,
                "value": lead_val,
                "unit": top_unit,
                "sparkline": sparkline_pts,
                "metrics": dev_metrics,
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
        "apparent_power": {"name": "Scheinleistung", "unit": "VA", "icon": "⚡"},
        "reactive_power": {"name": "Blindleistung", "unit": "var", "icon": "⚡"},
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
        "soh": {"name": "Batteriegesundheit", "unit": "%", "icon": "🩺"},
        "energy": {"name": "Energie", "unit": "kWh", "icon": "📊"},
        "energy_import": {"name": "Netzbezug", "unit": "kWh", "icon": "📥"},
        "energy_export": {"name": "Einspeisung", "unit": "kWh", "icon": "📤"},
        "frequency": {"name": "Frequenz", "unit": "Hz", "icon": "〰️"},
        "power_factor": {"name": "Leistungsfaktor", "unit": "", "icon": "📐"},
        "temperature": {"name": "Temperatur", "unit": "°C", "icon": "🌡️"},
        "humidity": {"name": "Luftfeuchtigkeit", "unit": "%", "icon": "💧"},
        "pressure": {"name": "Luftdruck", "unit": "hPa", "icon": "⏲️"},
        "co2": {"name": "CO2-Gehalt", "unit": "ppm", "icon": "🫧"},
        "voc": {"name": "Luftgüte (VOC)", "unit": "ppb", "icon": "🍃"},
        "illuminance": {"name": "Helligkeit", "unit": "lx", "icon": "💡"},
        "solar_radiation": {"name": "Sonneneinstrahlung", "unit": "W/m²", "icon": "☀️"},
        "wind_speed": {"name": "Windgeschwindigkeit", "unit": "m/s", "icon": "💨"},
        "flow_temperature": {"name": "Vorlauftemperatur", "unit": "°C", "icon": "🔥"},
        "return_temperature": {"name": "Rücklauftemperatur", "unit": "°C", "icon": "❄️"},
        "flow_rate": {"name": "Durchfluss", "unit": "l/h", "icon": "🌊"},
        "heat_power": {"name": "Wärmeleistung", "unit": "kW", "icon": "♨️"},
        "percentage": {"name": "Prozentwert", "unit": "%", "icon": "📈"},
    }

    from devices.services.ingest import _infer_canonical_unit

    def_map = {d.key: d for d in MetricDefinition.objects.all()}
    cfg = getattr(device, "config", None)

    results = []
    seen_keys = set()
    configured_lead_key = cfg.metric_definition.key if (cfg and cfg.metric_definition) else None

    # Prüfen, ob das Gerät ein Multi-Source-Inverter ist (pv/battery/grid)
    all_raw_keys = {lm.metric_key.lower() for lm in latest_metrics}
    is_multi_source = any(k in all_raw_keys for k in ["pv_power", "grid_power", "battery_power", "load_power"])

    for lm in latest_metrics:
        k = lm.metric_key
        if k.startswith("state.") or k.startswith("daily_") or k in [
            "daily_charge_kwh", "daily_discharge_kwh", "daily_feed_in_kwh",
            "daily_generation_kwh", "daily_import_kwh"
        ]:
            continue

        # 1. Alias-Normalisierung: soc -> battery_soc
        if k.lower() in ["soc", "battery_level"]:
            k = "battery_soc"

        # 2. Generische Keys (value, val) auf konfigurierte Lead-Metrik mappen
        if k.lower() in ["value", "val"] and configured_lead_key:
            k = configured_lead_key

        # 3. Single-Channel Submeter / Verbraucher: generische 'power'/'temperature' Keys mit konfigurierter Lead-Metrik zusammenführen
        if not is_multi_source and configured_lead_key:
            cfg_lower = configured_lead_key.lower()
            k_lower = k.lower()
            if ("power" in cfg_lower or cfg_lower in ["aircon_power", "heatpump_power", "bwwp_power", "wallbox_power"]) and k_lower in ["power", "active_power", "p_total", "w", "watt", "value", "val"]:
                k = configured_lead_key
            elif "temp" in cfg_lower and k_lower in ["temperature", "temp", "device_temp", "value", "val"]:
                k = configured_lead_key

        # 4. Multi-Source Inverter: generisches 'power' ignorieren, wenn dedizierte Kanäle (pv_power/load_power) vorliegen
        if is_multi_source and k.lower() in ["power", "value", "val"] and "pv_power" in all_raw_keys:
            continue

        # 5. Strikte Deduplizierung: Bereits erfasste Kanäle überspringen
        if k in seen_keys:
            continue
        seen_keys.add(k)

        meta = KEY_METADATA.get(k, {})
        d_obj = def_map.get(k) or (cfg.metric_definition if cfg and cfg.metric_definition and cfg.metric_definition.key == k else None)

        # Intelligente Namens- und Icon-Zuordnung
        if d_obj and d_obj.name:
            name = d_obj.name
            icon = meta.get("icon", "🌡️" if "temp" in k.lower() else "📈")
        elif "temp" in k.lower():
            name = "Temperatur (" + k.replace("_", " ").title() + ")"
            icon = "🌡️"
        elif "power" in k.lower():
            name = "Leistung (" + k.replace("_", " ").title() + ")"
            icon = "⚡"
        else:
            name = meta.get("name", k.replace("_", " ").title())
            icon = meta.get("icon", "📈")

        unit = (d_obj.unit if d_obj else None) or lm.unit or _infer_canonical_unit(k, "", config=cfg)

        is_primary = (k == primary_key) or (primary_key not in seen_keys and k in ["power", "value", "active_power", "temperature", "bwwp_temp", configured_lead_key])

        val_to_use = lm.value
        cached_v = cache.get(f"device:{device_id}:{k}") or cache.get(f"device:{device_id}:{lm.metric_key}")
        if cached_v is not None:
            try:
                val_to_use = float(cached_v)
            except (ValueError, TypeError):
                pass

        results.append({
            "key": k,
            "name": name,
            "unit": unit,
            "icon": icon,
            "latest_value": round(float(val_to_use), 2) if val_to_use is not None else None,
            "timestamp": lm.timestamp.isoformat() if lm.timestamp else None,
            "is_primary": is_primary,
        })

    if not results:
        inferred_u = (cfg.metric_definition.unit if (cfg and cfg.metric_definition and cfg.metric_definition.unit) else None) or _infer_canonical_unit(primary_key, "", config=cfg)
        p_name = device.config.metric_definition.name if (cfg and cfg.metric_definition and cfg.metric_definition.name) else ("Temperatur" if "temp" in primary_key.lower() else "Leistung")
        p_icon = "🌡️" if "temp" in primary_key.lower() else "⚡"
        results.append({
            "key": primary_key,
            "name": p_name,
            "unit": inferred_u,
            "icon": p_icon,
            "latest_value": None,
            "timestamp": None,
            "is_primary": True,
        })

    return Response({"metrics": results, "primary_metric": primary_key})


@api_view(["GET"])
def device_timeseries(request, device_id):
    range_str = request.GET.get("range") or request.GET.get("period") or "24h"
    requested_metric = request.GET.get("metric")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    from devices.services.export_manager import get_device_timeseries_dataset

    device = get_object_or_404(
        Device.objects.select_related("home", "config__metric_definition"),
        id=device_id,
    )

    dataset = get_device_timeseries_dataset(
        device=device,
        range_str=range_str,
        requested_metric=requested_metric,
        start_date=start_date,
        end_date=end_date,
    )

    return Response(
        {
            "device": device_id,
            "range": range_str,
            "period_label": dataset["period_label"],
            "metric": dataset["metric_key"],
            "metric_name": dataset["metric_name"],
            "unit": dataset["unit"],
            "stats": dataset["stats"],
            "points": [
                {
                    "t": p["t"],
                    "v": p["v"],
                    "min": p["min"],
                    "max": p["max"],
                }
                for p in dataset["points"]
            ],
        }
    )


@api_view(["GET"])
def export_device_timeseries_view(request, device_id):
    export_format = (
        request.GET.get("export_format")
        or request.GET.get("format")
        or "xlsx"
    ).lower()
    range_str = request.GET.get("range") or request.GET.get("period") or "24h"
    metric = request.GET.get("metric")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    from devices.services.export_manager import export_device_timeseries

    return export_device_timeseries(
        user=request.user,
        device_id=device_id,
        range_str=range_str,
        requested_metric=metric,
        start_date=start_date,
        end_date=end_date,
        export_format=export_format,
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
    device_ids = request.data.get("device_ids", [])
    delete_after = timezone.now() + timedelta(days=30)

    updated = Device.objects.filter(
        id__in=device_ids,
        home__user=request.user,
    ).update(
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


# ============================================================
# ✅ SIMULATE DEVICE TELEMETRY (für Onboarding & Live-Test)
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def simulate_telemetry(request, device_id):
    device = get_object_or_404(
        Device.objects.select_related("config__metric_definition"),
        id=device_id,
        home__user=request.user,
    )

    value = float(request.data.get("value", 450.0))
    metric_key = request.data.get("metric_key")
    if not metric_key:
        if hasattr(device, "config") and device.config and device.config.metric_definition:
            metric_key = device.config.metric_definition.key
        else:
            metric_key = "power"

    from devices.services.ingest import ingest_metric_payload

    result = ingest_metric_payload(
        device=device,
        metrics={metric_key: value},
        source="simulator",
    )

    return Response({
        "status": "ok",
        "device_id": device.id,
        "metric": metric_key,
        "value": value,
        "result": result,
    })


# ============================================================
# ✅ REGENERATE MQTT PASSWORD
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def regenerate_mqtt_password(request):
    home = request.user.homes.first()
    if not home:
        return Response({"error": "No home found"}, status=404)

    import secrets
    home.mqtt_password = secrets.token_hex(16)
    home.save(update_fields=["mqtt_password"])

    from devices.tasks import provision_home
    provision_home.delay(home.id)

    return Response(HomeSerializer(home).data)


# ============================================================
# ✅ BIDIRECTIONAL RELAY SWITCHING (ACTUATION)
# ============================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def device_switch(request, device_id):
    """
    Schaltet das Relais eines Geräts (Shelly WSS / MQTT / Smart Plug) ein, aus oder toggelt es.
    Body:
    {
        "state": "on" | "off" | "toggle",
        "channel": 0
    }
    """
    import logging
    from django.core.cache import cache
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    logger = logging.getLogger(__name__)
    device = get_object_or_404(Device, id=device_id)

    # Berechtigungsprüfung
    user_homes = request.user.homes.all()
    if device.home not in user_homes and not request.user.is_staff and not request.user.is_superuser:
        return Response({"error": "Keine Berechtigung für dieses Gerät."}, status=403)

    state = str(request.data.get("state", "toggle")).lower().strip()
    channel = int(request.data.get("channel", 0))

    if state not in ("on", "off", "toggle", "true", "false", "1", "0"):
        return Response({"error": "Ungültiger Zustand. Erlaubt sind 'on', 'off' oder 'toggle'."}, status=400)

    if state in ("true", "1"):
        state = "on"
    elif state in ("false", "0"):
        state = "off"

    # 1. Ermittle neuen Zielzustand
    current_state = cache.get(f"device_relay_state_{device.id}", False)
    if state == "toggle":
        target_state = not current_state
        cmd = "on" if target_state else "off"
    else:
        target_state = (state == "on")
        cmd = state

    # 2. Cache sofort optimistisch aktualisieren
    cache.set(f"device_relay_state_{device.id}", target_state, timeout=3600)
    cache.set(f"device_switchable_{device.id}", True, timeout=86400)

    # 3. Befehl über Channels Layer an den verbundenen WebSocket (Daphne) senden
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                f"device_{device.id}",
                {
                    "type": "relay_command",
                    "command": cmd,
                    "channel": channel,
                },
            )
            async_to_sync(channel_layer.group_send)(
                f"device_{device.identifier}",
                {
                    "type": "relay_command",
                    "command": cmd,
                    "channel": channel,
                },
            )
        except Exception as e:
            logger.warning("[Device-Switch] Fehler beim Senden an Channel-Layer: %s", e)

    logger.info("[Device-Switch] ⚡ Relais für %s (ID: %s) geschaltet: %s -> %s (Kanal: %s)", device.identifier, device.id, current_state, target_state, channel)

    return Response({
        "status": "success",
        "device_id": device.id,
        "identifier": device.identifier,
        "relay_state": target_state,
        "command": cmd,
        "channel": channel,
    })


# ============================================================
# 🧠 GERÄTEPROFILING & BASELINE API
# ============================================================

@api_view(["GET", "POST", "PATCH"])
@permission_classes([IsAuthenticated])
def device_baseline_profile_view(request, device_id):
    """
    Liefert oder aktualisiert das Baseline-Profil eines Geräts.
    """
    from devices.services_profiling import (
        get_or_create_device_profile,
        evaluate_device_baseline,
        APPLIANCE_PRESETS,
    )

    device = get_object_or_404(Device, id=device_id)
    user_homes = request.user.homes.all()
    if device.home not in user_homes and not request.user.is_staff and not request.user.is_superuser:
        return Response({"error": "Keine Berechtigung für dieses Gerät."}, status=403)

    profile = get_or_create_device_profile(device)

    if request.method in ["POST", "PATCH"]:
        data = request.data
        if "appliance_type" in data:
            profile.appliance_type = data["appliance_type"]
            # Bei Typ-Wechsel Preset übernehmen, sofern nicht explizit überschrieben
            if data.get("apply_preset", False) and profile.appliance_type in APPLIANCE_PRESETS:
                p = APPLIANCE_PRESETS[profile.appliance_type]
                profile.standby_power_w = p["standby_power_w"]
                profile.standby_tolerance_pct = p["standby_tolerance_pct"]
                profile.standby_max_w = p["standby_max_w"]
                profile.operating_power_min_w = p["operating_power_min_w"]
                profile.operating_power_max_w = p["operating_power_max_w"]
                profile.max_continuous_run_hours = p["max_continuous_run_hours"]

        if "is_active" in data:
            profile.is_active = bool(data["is_active"])
        if "standby_power_w" in data:
            profile.standby_power_w = float(data["standby_power_w"])
        if "standby_tolerance_pct" in data:
            profile.standby_tolerance_pct = float(data["standby_tolerance_pct"])
        if "standby_max_w" in data:
            profile.standby_max_w = float(data["standby_max_w"])
        if "operating_power_min_w" in data:
            profile.operating_power_min_w = float(data["operating_power_min_w"])
        if "operating_power_max_w" in data:
            profile.operating_power_max_w = float(data["operating_power_max_w"])
        if "max_continuous_run_hours" in data:
            profile.max_continuous_run_hours = float(data["max_continuous_run_hours"])

        profile.save()
        # Sofortige Evaluierung anstoßen
        evaluate_device_baseline(device)
        profile.refresh_from_db()

    return Response({
        "id": str(profile.id),
        "device_id": device.id,
        "appliance_type": profile.appliance_type,
        "appliance_label": profile.get_appliance_type_display(),
        "is_active": profile.is_active,
        "standby_power_w": profile.standby_power_w,
        "standby_tolerance_pct": profile.standby_tolerance_pct,
        "standby_max_w": profile.standby_max_w,
        "operating_power_min_w": profile.operating_power_min_w,
        "operating_power_max_w": profile.operating_power_max_w,
        "max_continuous_run_hours": profile.max_continuous_run_hours,
        "learning_mode": profile.learning_mode,
        "current_health_status": profile.current_health_status,
        "last_measured_standby_w": profile.last_measured_standby_w,
        "last_measured_operating_w": profile.last_measured_operating_w,
        "anomaly_reason": profile.anomaly_reason,
        "last_evaluated_at": profile.last_evaluated_at.isoformat() if profile.last_evaluated_at else None,
        "presets": APPLIANCE_PRESETS,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def device_baseline_learn_view(request, device_id):
    """
    Lernt automatisch die Baseline aus den realen Messwerten der letzten N Tage.
    """
    from devices.services_profiling import learn_device_baseline, evaluate_device_baseline

    device = get_object_or_404(Device, id=device_id)
    user_homes = request.user.homes.all()
    if device.home not in user_homes and not request.user.is_staff and not request.user.is_superuser:
        return Response({"error": "Keine Berechtigung für dieses Gerät."}, status=403)

    days = int(request.data.get("days", 7))
    profile = learn_device_baseline(device, days=days)
    eval_res = evaluate_device_baseline(device)
    profile.refresh_from_db()

    return Response({
        "status": "success",
        "message": f"Baseline aus {days} Tagen erfolgreich gelernt.",
        "standby_power_w": profile.standby_power_w,
        "standby_max_w": profile.standby_max_w,
        "operating_power_min_w": profile.operating_power_min_w,
        "operating_power_max_w": profile.operating_power_max_w,
        "evaluation": eval_res,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def device_baseline_evaluate_view(request, device_id):
    """
    Führt eine manuelle Baseline-Prüfung durch.
    """
    from devices.services_profiling import evaluate_device_baseline

    device = get_object_or_404(Device, id=device_id)
    user_homes = request.user.homes.all()
    if device.home not in user_homes and not request.user.is_staff and not request.user.is_superuser:
        return Response({"error": "Keine Berechtigung für dieses Gerät."}, status=403)

    eval_res = evaluate_device_baseline(device)
    return Response(eval_res)




