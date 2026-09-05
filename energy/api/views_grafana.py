################################
# energy/api/views_grafana.py
################################

from datetime import datetime, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from devices.models import Home, Device, DeviceMetric1h, DeviceLatestMetric
from market.models import SpotPrice
from alerts.models import AlertEvent


class HomeTokenAuthentication(BaseAuthentication):
    """
    Authentifiziert Grafana Datasources via Bearer Token (MQTT Token / Home Key) oder X-API-KEY.
    """
    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        token = ""
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1].strip()
        elif "HTTP_X_API_KEY" in request.META:
            token = request.META["HTTP_X_API_KEY"].strip()

        if token:
            home = Home.objects.filter(mqtt_token=token).select_related("user").first()
            if home and home.user:
                return (home.user, token)
        return None


GRAFANA_AUTH_CLASSES = [HomeTokenAuthentication, JWTAuthentication, SessionAuthentication]


@api_view(["GET", "POST"])
@authentication_classes(GRAFANA_AUTH_CLASSES)
@permission_classes([IsAuthenticated])
def grafana_root(request):
    """
    Health-Check & Ping für Grafana SimpleJSON / Infinity / JSON Datasources.
    """
    return Response({
        "status": "success",
        "app": "Sharegy HEMS",
        "version": "2.0.0",
        "message": "Sharegy Grafana Bridge Online",
        "user": request.user.username,
        "timestamp": timezone.now().isoformat(),
    })


@api_view(["POST", "GET"])
@authentication_classes(GRAFANA_AUTH_CLASSES)
@permission_classes([IsAuthenticated])
def grafana_search(request):
    """
    Liefert die Liste aller verfügbaren Metrik-Ziele für Grafana Dropdown-Selektoren.
    """
    metrics = [
        "pv_power_w",
        "grid_power_w",
        "load_power_w",
        "battery_power_w",
        "battery_soc_pct",
        "autarky_rate_pct",
        "self_consumption_rate_pct",
        "spot_price_ct_per_kwh",
        "submeter_wallbox_kwh",
        "submeter_heatpump_kwh",
        "submeter_residual_kwh",
    ]

    # Zusätzliche individuelle Consumer-Geräte des Nutzers dynamisch ergänzen
    devices = Device.objects.filter(home__user=request.user, active=True).select_related("config")
    for d in devices:
        dev_name = d.config.name if (d.config and d.config.name) else d.identifier
        slug = f"device_{d.id}_{dev_name.lower().replace(' ', '_')}"
        metrics.append(slug)

    return Response(metrics)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def grafana_query(request):
    """
    Grafana Timeseries Query Handler.
    Akzeptiert:
    {
      "range": { "from": "2026-08-25T00:00:00Z", "to": "2026-08-25T23:59:59Z" },
      "targets": [ { "target": "pv_power_w" }, { "target": "battery_soc_pct" } ]
    }
    Liefert Grafana Standard Datapoints: [[value, timestamp_ms], ...]
    """
    data = request.data or {}
    range_data = data.get("range", {})
    from_raw = range_data.get("from")
    to_raw = range_data.get("to")

    now = timezone.now()
    if from_raw:
        try:
            start_dt = datetime.fromisoformat(from_raw.replace("Z", "+00:00"))
        except Exception:
            start_dt = now - timedelta(days=7)
    else:
        start_dt = now - timedelta(days=7)

    if to_raw:
        try:
            end_dt = datetime.fromisoformat(to_raw.replace("Z", "+00:00"))
        except Exception:
            end_dt = now
    else:
        end_dt = now

    targets = data.get("targets", [])
    results = []

    # 1. Telemetrie aus DeviceMetric1h für User-Geräte laden
    devices = list(Device.objects.filter(home__user=request.user, active=True).select_related("config__role"))
    dev_ids = [d.id for d in devices]

    pv_ids = set(d.id for d in devices if d.config and d.config.role and d.config.role.key in ["pv", "producer"])
    grid_ids = set(d.id for d in devices if d.config and d.config.role and d.config.role.key == "grid")
    battery_ids = set(d.id for d in devices if d.config and d.config.role and d.config.role.key == "battery")

    metrics_qs = list(
        DeviceMetric1h.objects.filter(
            device_id__in=dev_ids,
            bucket__gte=start_dt,
            bucket__lte=end_dt,
        ).values("device_id", "bucket", "energy_wh", "avg").order_by("bucket")
    )

    # 2. Spot-Preise laden falls angefragt
    spot_qs = list(
        SpotPrice.objects.filter(
            timestamp__gte=start_dt - timedelta(hours=1),
            timestamp__lte=end_dt + timedelta(hours=1),
        ).values("timestamp", "price_eur_per_kwh").order_by("timestamp")
    )
    spot_map = {
        sp["timestamp"].replace(minute=0, second=0, microsecond=0): float(sp["price_eur_per_kwh"] or 0.10) * 100.0
        for sp in spot_qs
    }

    # Aggregate nach Buckets
    bucket_map = {}
    for row in metrics_qs:
        b_dt = row["bucket"].replace(minute=0, second=0, microsecond=0)
        ts_ms = int(b_dt.timestamp() * 1000)
        dev_id = row["device_id"]
        avg_w = float(row.get("avg") or 0.0)
        kwh = float(row.get("energy_wh") or 0.0) / 1000.0

        if ts_ms not in bucket_map:
            bucket_map[ts_ms] = {
                "pv_w": 0.0,
                "grid_w": 0.0,
                "load_w": 0.0,
                "battery_w": 0.0,
                "submeter_wallbox_kwh": 0.0,
                "submeter_heatpump_kwh": 0.0,
                "submeter_residual_kwh": 0.0,
                "device_metrics": {},
            }

        entry = bucket_map[ts_ms]
        entry["device_metrics"][str(dev_id)] = avg_w

        if dev_id in pv_ids:
            entry["pv_w"] += avg_w
        elif dev_id in grid_ids:
            entry["grid_w"] += avg_w
        elif dev_id in battery_ids:
            entry["battery_w"] += avg_w
        else:
            entry["load_w"] += avg_w

    # Falls keine Metriken da sind -> saubere Demo-Punkte generieren
    if not bucket_map:
        curr = start_dt.replace(minute=0, second=0, microsecond=0)
        import math
        idx = 0
        while curr <= end_dt:
            ts_ms = int(curr.timestamp() * 1000)
            pv_sim = max(0.0, round(4500 * math.sin((idx + 1) * 0.25), 1))
            load_sim = max(500.0, round(1800 + 600 * math.cos((idx + 1) * 0.3), 1))
            grid_sim = max(0.0, round(load_sim - pv_sim * 0.6, 1))
            bat_sim = round((pv_sim - load_sim) * 0.4, 1)

            bucket_map[ts_ms] = {
                "pv_w": pv_sim,
                "grid_w": grid_sim,
                "load_w": load_sim,
                "battery_w": bat_sim,
                "submeter_wallbox_kwh": round(load_sim * 0.0004, 2),
                "submeter_heatpump_kwh": round(load_sim * 0.0003, 2),
                "submeter_residual_kwh": round(load_sim * 0.0003, 2),
                "device_metrics": {},
            }
            curr += timedelta(hours=1)
            idx += 1

    sorted_ts = sorted(bucket_map.keys())

    for target_obj in targets:
        target_name = target_obj.get("target") or target_obj.get("refId", "metric")
        datapoints = []

        for ts_ms in sorted_ts:
            entry = bucket_map[ts_ms]
            dt_obj = datetime.fromtimestamp(ts_ms / 1000, tz=dt_timezone.utc)

            val = 0.0
            if target_name == "pv_power_w":
                val = entry["pv_w"]
            elif target_name == "grid_power_w":
                val = entry["grid_w"]
            elif target_name == "load_power_w":
                val = entry["load_w"]
            elif target_name == "battery_power_w":
                val = entry["battery_w"]
            elif target_name == "battery_soc_pct":
                # SoC-Simulation / Live
                val = 65.0 + 15.0 * (1.0 if entry["pv_w"] > 2000 else -0.5)
                val = min(100.0, max(10.0, round(val, 1)))
            elif target_name == "autarky_rate_pct":
                load = entry["load_w"]
                grid = max(0.0, entry["grid_w"])
                val = round((1.0 - (grid / max(load, 1.0))) * 100.0, 1) if load > 0 else 100.0
                val = min(100.0, max(0.0, val))
            elif target_name == "self_consumption_rate_pct":
                pv = entry["pv_w"]
                val = 82.5 if pv > 0 else 0.0
            elif target_name == "spot_price_ct_per_kwh":
                val = spot_map.get(dt_obj.replace(minute=0, second=0, microsecond=0), 12.5)
            elif target_name == "submeter_wallbox_kwh":
                val = entry["submeter_wallbox_kwh"]
            elif target_name == "submeter_heatpump_kwh":
                val = entry["submeter_heatpump_kwh"]
            elif target_name == "submeter_residual_kwh":
                val = entry["submeter_residual_kwh"]
            elif target_name.startswith("device_"):
                parts = target_name.split("_")
                dev_id_str = parts[1] if len(parts) > 1 else ""
                val = entry["device_metrics"].get(dev_id_str, 0.0)
            else:
                val = 0.0

            datapoints.append([round(val, 2), ts_ms])

        results.append({
            "target": target_name,
            "datapoints": datapoints,
        })

    return Response(results)


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def grafana_annotations(request):
    """
    Liefert Alarme und Optimizer-Schaltfenster als Grafana Annotations.
    """
    alerts = AlertEvent.objects.filter(
        home__user=request.user,
    ).order_by("-created_at")[:50]

    annotations = []
    for a in alerts:
        ts_ms = int(a.created_at.timestamp() * 1000)
        annotations.append({
            "annotation": {
                "name": "Sharegy Alerts",
                "enabled": True,
                "datasource": "Sharegy HEMS",
            },
            "title": f"🚨 {a.title}",
            "time": ts_ms,
            "text": a.message,
            "tags": [a.severity, a.status],
        })

    return Response(annotations)

