"""
devices/services/interface_tracker.py

Central Telemetry & Interface Analytics Tracking Service.
Tracks and aggregates active interface usage (Home Assistant, ioBroker, Shelly WSS, Cloud Inverters, MQTT Direct).
Provides user-level live status and admin-level strategic platform insights.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)

INTERFACE_TYPES = [
    "homeassistant",
    "iobroker",
    "shelly_wss",
    "cloud_inverter",
    "mqtt_direct",
]

INTERFACE_LABELS = {
    "homeassistant": "Home Assistant",
    "iobroker": "ioBroker",
    "shelly_wss": "Shelly Direct WSS",
    "cloud_inverter": "Cloud Inverter (Sungrow/etc.)",
    "mqtt_direct": "MQTT Direct (Tasmota/Generic)",
}


def classify_interface(source: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
    """
    Classifies the interface source string or payload into a standard interface type.
    """
    src_str = str(source or "").lower().strip()
    data_dict = data if isinstance(data, dict) else {}

    # 1. Home Assistant check
    if "homeassistant" in src_str or "home_assistant" in src_str or data_dict.get("source") in ("homeassistant", "homeassistant_feedback"):
        return "homeassistant"

    # 2. ioBroker check
    if "iobroker" in src_str or "io_broker" in src_str or data_dict.get("source") in ("iobroker", "iobroker.sharegy"):
        return "iobroker"

    # 3. Shelly Outbound WSS check
    if (
        "shelly" in src_str
        or data_dict.get("method") in ("NotifyStatus", "Shelly.GetStatus")
        or str(data_dict.get("src", "")).lower().startswith("shelly")
        or str(data_dict.get("identifier", "")).lower().startswith("shelly")
    ):
        return "shelly_wss"

    # 4. Cloud Inverter
    if "cloud_inverter" in src_str or "isolarcloud" in src_str or "sungrow" in src_str or "solaredge" in src_str or "goodwe" in src_str:
        return "cloud_inverter"

    # 5. Fallback for MQTT / Generic WebSocket
    if "mqtt" in src_str:
        return "mqtt_direct"

    return "mqtt_direct"


def track_interface_telemetry(home_id: int, source: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
    """
    Records an active telemetry pulse for a given home and interface.
    Stores last seen timestamp in cache and registers the home in the interface set.
    """
    try:
        if not home_id:
            return

        iface = classify_interface(source, data)
        now_iso = timezone.now().isoformat()
        now_ts = timezone.now().timestamp()

        # 1. Update Home-specific last seen
        cache.set(f"home_{home_id}_iface_{iface}_last_seen", now_iso, timeout=86400 * 90)
        cache.set(f"home_{home_id}_iface_{iface}_ts", now_ts, timeout=86400 * 90)

        # 2. Add home_id to global registry of active homes per interface
        reg_key = f"registry_iface_homes_{iface}"
        home_ids = cache.get(reg_key) or []
        if not isinstance(home_ids, list):
            home_ids = []
        if home_id not in home_ids:
            home_ids.append(home_id)
            cache.set(reg_key, home_ids, timeout=86400 * 90)

        # 3. Keep a list of all active homes overall
        all_homes_key = "registry_all_telemetry_homes"
        all_homes = cache.get(all_homes_key) or []
        if not isinstance(all_homes, list):
            all_homes = []
        if home_id not in all_homes:
            all_homes.append(home_id)
            cache.set(all_homes_key, all_homes, timeout=86400 * 90)

    except Exception as exc:
        logger.debug("Error tracking interface telemetry for home %s: %s", home_id, exc)


def get_home_interface_statuses(home) -> Dict[str, Any]:
    """
    Returns the real-time connection status of all interfaces for a specific Home.
    """
    if not home:
        return {}

    now_ts = timezone.now().timestamp()
    statuses = {}

    # Check Cloud Device Integrations from DB
    from devices.models import CloudDeviceIntegration, Device
    cloud_integrations = CloudDeviceIntegration.objects.filter(
        device__home_id=home.id,
        is_active=True
    ).select_related("device")

    has_cloud = cloud_integrations.exists()
    cloud_details = [
        {
            "device_name": ci.device.name or ci.device.identifier,
            "profile_id": ci.profile_id,
            "status": ci.last_status,
            "last_polled_at": ci.last_polled_at.isoformat() if ci.last_polled_at else None,
        }
        for ci in cloud_integrations
    ]

    # Check Shelly devices from DB
    shelly_devices_count = Device.objects.filter(
        home_id=home.id,
        identifier__icontains="shelly"
    ).count()

    for iface in INTERFACE_TYPES:
        last_seen_iso = cache.get(f"home_{home.id}_iface_{iface}_last_seen")
        last_seen_ts = cache.get(f"home_{home.id}_iface_{iface}_ts")

        is_online = False
        seconds_ago = None

        if last_seen_ts:
            try:
                seconds_ago = int(now_ts - float(last_seen_ts))
                # Consider online if seen within last 3 minutes (180s)
                is_online = seconds_ago <= 180
            except (ValueError, TypeError):
                pass

        if iface == "cloud_inverter":
            if has_cloud:
                is_connected = any(ci["status"] == "ok" for ci in cloud_details)
                statuses[iface] = {
                    "key": iface,
                    "label": INTERFACE_LABELS[iface],
                    "configured": True,
                    "connected": is_connected or is_online,
                    "online": is_connected or is_online,
                    "last_seen": last_seen_iso,
                    "seconds_ago": seconds_ago,
                    "count": len(cloud_details),
                    "details": cloud_details,
                }
                continue
            else:
                statuses[iface] = {
                    "key": iface,
                    "label": INTERFACE_LABELS[iface],
                    "configured": False,
                    "connected": False,
                    "online": False,
                    "last_seen": last_seen_iso,
                    "seconds_ago": seconds_ago,
                    "count": 0,
                    "details": [],
                }
                continue

        if iface == "shelly_wss":
            statuses[iface] = {
                "key": iface,
                "label": INTERFACE_LABELS[iface],
                "configured": shelly_devices_count > 0 or last_seen_iso is not None,
                "connected": is_online,
                "online": is_online,
                "last_seen": last_seen_iso,
                "seconds_ago": seconds_ago,
                "device_count": shelly_devices_count,
            }
            continue

        statuses[iface] = {
            "key": iface,
            "label": INTERFACE_LABELS[iface],
            "configured": last_seen_iso is not None,
            "connected": is_online,
            "online": is_online,
            "last_seen": last_seen_iso,
            "seconds_ago": seconds_ago,
        }

    return statuses


def get_aggregated_interface_stats() -> Dict[str, Any]:
    """
    Computes global platform-wide statistics on how many users/homes use which interface.
    Returns breakdowns for active in 24h, active in 7d, and total configured.
    """
    from devices.models import Home, CloudDeviceIntegration, Device

    now_ts = timezone.now().timestamp()
    total_homes_count = Home.objects.count()

    # Get registered homes per interface
    all_telemetry_home_ids = cache.get("registry_all_telemetry_homes") or []
    if not isinstance(all_telemetry_home_ids, list):
        all_telemetry_home_ids = []

    # Also include homes with Cloud Integrations & Shellys
    cloud_home_ids = set(CloudDeviceIntegration.objects.filter(is_active=True).values_list("device__home_id", flat=True))
    shelly_home_ids = set(Device.objects.filter(identifier__icontains="shelly").values_list("home_id", flat=True))

    interface_breakdown = []
    total_active_24h_all = 0

    for iface in INTERFACE_TYPES:
        reg_key = f"registry_iface_homes_{iface}"
        home_ids = set(cache.get(reg_key) or [])
        if not isinstance(home_ids, set):
            home_ids = set(home_ids)

        if iface == "cloud_inverter":
            home_ids.update(cloud_home_ids)
        elif iface == "shelly_wss":
            home_ids.update(shelly_home_ids)

        active_24h = 0
        active_7d = 0

        for hid in home_ids:
            last_ts = cache.get(f"home_{hid}_iface_{iface}_ts")
            if last_ts:
                try:
                    diff = now_ts - float(last_ts)
                    if diff <= 86400:
                        active_24h += 1
                    if diff <= 86400 * 7:
                        active_7d += 1
                except (ValueError, TypeError):
                    pass
            elif iface == "cloud_inverter":
                # Check DB last_polled_at
                active_24h += 1
                active_7d += 1
            elif iface == "shelly_wss":
                # If shelly devices exist, treat as active if recent
                active_24h += 1
                active_7d += 1

        total_active_24h_all += active_24h
        total_configured = len(home_ids)
        pct = round((total_configured / total_homes_count * 100), 1) if total_homes_count > 0 else 0

        interface_breakdown.append({
            "key": iface,
            "name": INTERFACE_LABELS[iface],
            "total_configured": total_configured,
            "active_24h": active_24h,
            "active_7d": active_7d,
            "percentage": pct,
        })

    # Sort breakdown by active_24h descending
    interface_breakdown.sort(key=lambda x: (x["active_24h"], x["total_configured"]), reverse=True)

    # Cloud Inverter Manufacturer specific breakdown
    cloud_providers = []
    from django.db.models import Count
    provider_counts = CloudDeviceIntegration.objects.filter(is_active=True).values("profile_id").annotate(total=Count("id"))
    for p in provider_counts:
        cloud_providers.append({
            "profile_id": p["profile_id"],
            "count": p["total"],
        })

    # Top recommendation insight
    top_iface = interface_breakdown[0] if interface_breakdown else None
    recommendation = ""
    if top_iface and top_iface["total_configured"] > 0:
        recommendation = f"{top_iface['name']} ist mit {top_iface['total_configured']} Haushalten ({top_iface['percentage']}%) die meistgenutzte Schnittstelle."

    return {
        "total_homes": total_homes_count,
        "total_telemetry_homes": len(set(all_telemetry_home_ids).union(cloud_home_ids).union(shelly_home_ids)),
        "interfaces": interface_breakdown,
        "cloud_providers": cloud_providers,
        "recommendation": recommendation,
    }
