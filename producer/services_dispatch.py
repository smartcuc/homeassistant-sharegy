"""
producer/services_dispatch.py

Automatisierte Bi-Direktionale Speicher-Steuerung (Arbitrage-Dispatch).
Prüft stündlich/zyklisch für alle aktiven Batteriespeicher im Modus 'price_optimized':
1. Liegt die aktuelle Stunde im günstigsten Ladefenster (oder unter dem Preisschwellenwert)?
2. Ist der Speicher noch aufnahmefähig (SoC < 95 %)?
-> Schaltet automatisch auf Netzladung (forced_charge mit Soll-Ladeleistung in kW).
-> Schaltet nach Ablauf des Preisfensters oder bei vollem Akku automatisch zurück auf PV-Autarkie (self_consumption).
-> Sendet Steuerbefehle an Wechselrichter (Sungrow, MQTT, WSS/Home Assistant Bridge).
"""

import logging
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from django.core.cache import cache

from producer.models import StorageSystem
from devices.models import Device, DeviceLatestMetric
from energy.services.battery_arbitrage import calculate_battery_arbitrage
from market.models_tariff import HomeTariff
from market.services_tariff import get_home_tariff
from market.models import SpotPrice

logger = logging.getLogger("producer.dispatch")


def dispatch_inverter_write_command(storage: StorageSystem, action: str, power_kw: float) -> dict:
    """
    Sendet den Steuerbefehl über alle verfügbaren Schnittstellen an den Wechselrichter/Speicher:
    1. Channels WebSocket Event (an aktive Home / Device WSS Clients)
    2. MQTT Publisher (an lokales Gateway / ioBroker / Home Assistant)
    3. Redis Cache für lokale Poller & Realtime-Status
    """
    home = storage.home
    power_watts = int(power_kw * 1000)
    now = timezone.now()

    payload = {
        "ts": now.isoformat(),
        "storage_id": str(storage.id),
        "storage_name": storage.name,
        "action": action, # "forced_charge" | "self_consumption" | "forced_discharge" | "idle"
        "power_kw": float(power_kw),
        "power_w": power_watts,
        "mode_code": 1 if action == "forced_charge" else (0 if action == "self_consumption" else 2),
    }

    # 1. In Redis Caches aktualisieren
    try:
        cache.set(f"storage:{storage.id}:active_dispatch_action", action, timeout=86400)
        cache.set(f"storage:{storage.id}:dispatch_power_kw", float(power_kw), timeout=86400)
        cache.set(f"storage:{storage.id}:last_dispatch_ts", now.isoformat(), timeout=86400)
    except Exception as e:
        logger.warning("Failed to update storage cache: %s", e)

    # 2. Django Channels Broadcast an WebSocket Clients (Daphne WSS)
    import sys
    is_testing = "test" in sys.argv or getattr(settings, "TESTING", False)

    if not is_testing:
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            if channel_layer and home:
                async_to_sync(channel_layer.group_send)(
                    f"home_{home.id}",
                    {
                        "type": "storage_command",
                        "payload": payload,
                    }
                )
        except Exception as e:
            logger.warning("Failed to send channels storage_command: %s", e)

        # 3. MQTT Publish (falls MQTT konfiguriert ist)
        try:
            from energy.mqtt_publisher import MqttPublisher
            mqtt_token = home.mqtt_token if home and hasattr(home, "mqtt_token") else "system"
            topic = f"h/{mqtt_token}/storage/{storage.id}/set"
            pub = MqttPublisher()
            pub.publish_json(topic, payload, qos=1, retain=False)
        except Exception as e:
            logger.debug("MQTT storage publish bypassed or failed: %s", e)

    # 3. Sungrow Cloud OpenAPI Steuerung ausführen (falls angebunden)
    sungrow_res = None
    try:
        from producer.services_sungrow_control import send_sungrow_cloud_control_command
        sungrow_res = send_sungrow_cloud_control_command(storage, action, power_kw)
    except Exception as e:
        logger.warning("Sungrow cloud control dispatch failed: %s", e)

    # TODO (Backlog): Lokale Home Assistant & ioBroker Outbound Modbus-Bridge anbinden
    # Dieser Baustein wird separat umgesetzt.

    return {
        "status": "dispatched",
        "storage_id": str(storage.id),
        "action": action,
        "power_kw": float(power_kw),
        "payload": payload,
        "sungrow_result": sungrow_res,
    }


def evaluate_and_dispatch_storage_system(storage: StorageSystem, now: datetime = None) -> dict:
    """
    Evaluiert ein einzelnes Speichersystem und führt bei Bedarf eine automatische
    Arbitrage-Ladung oder Rückstellung durch.
    """
    if now is None:
        now = timezone.now()

    home = storage.home
    if not storage.active:
        return {"dispatched": False, "reason": "storage_inactive"}

    if not storage.ems_control_enabled:
        return {"dispatched": False, "reason": "ems_control_disabled"}

    # 1. Aktuellen Ladestand (SoC) ermitteln
    soc = None
    soc_cache = cache.get(f"storage:{storage.id}:latest_soc")
    if soc_cache is not None:
        try:
            soc = float(soc_cache)
        except (ValueError, TypeError):
            pass

    if soc is None:
        soc_metric = (
            DeviceLatestMetric.objects.filter(device__home=home, metric_key__in=["battery_soc", "soc"])
            .order_by("-timestamp")
            .first()
        )
        if soc_metric:
            soc = float(soc_metric.value)
        else:
            soc = 50.0  # Fallback-Annahme

    current_hour = now.hour
    active_dispatch = cache.get(f"storage:{storage.id}:active_dispatch_action")

    # =========================================================================
    # MODUS 1: PREISGEFÜHRT (EPEX Spot / Tibber Arbitrage)
    # =========================================================================
    if storage.control_mode == "price_optimized":
        user = home.user if home else None
        arbitrage_data = calculate_battery_arbitrage(user) if user else {}
        best_charge_win = arbitrage_data.get("best_charge_window") or {}
        win_start_hour = best_charge_win.get("start_hour")
        win_end_hour = best_charge_win.get("end_hour")

        # Aktuellen Börsenpreis / Tarifpreis ermitteln
        today = now.date()
        tariff = get_home_tariff(home, today) if home else None
        current_spot = (
            SpotPrice.objects.filter(timestamp__lte=now)
            .order_by("-timestamp")
            .first()
        )
        spot_eur_kwh = float(current_spot.price_eur_per_kwh) if current_spot else 0.15
        spot_ct_kwh = spot_eur_kwh * 100.0

        is_in_charge_window = False
        if win_start_hour is not None and win_end_hour is not None:
            if win_start_hour <= win_end_hour:
                is_in_charge_window = win_start_hour <= current_hour < win_end_hour
            else:
                # Über Mitternacht (z. B. 23:00 - 04:00)
                is_in_charge_window = current_hour >= win_start_hour or current_hour < win_end_hour

        # Preis unter manueller Schwelle?
        threshold = float(storage.price_threshold_ct or 15.0)
        is_below_threshold = spot_ct_kwh <= threshold

        should_charge = (is_in_charge_window or is_below_threshold) and soc < 95.0

        if should_charge:
            target_power = float(storage.target_charge_power_kw or 3.0)
            cmd_text = f"AUTO: Netzladung aktiv ({target_power} kW) bei {spot_ct_kwh:.1f} ct/kWh (SoC={soc:.0f}%)"
            storage.last_control_command = cmd_text
            storage.last_controlled_at = now
            storage.save(update_fields=["last_control_command", "last_controlled_at"])

            dispatch_res = dispatch_inverter_write_command(storage, "forced_charge", target_power)
            logger.info("Storage %s: %s", storage.id, cmd_text)
            return {
                "dispatched": True,
                "action": "forced_charge",
                "power_kw": target_power,
                "command": cmd_text,
                "dispatch_result": dispatch_res,
            }
        else:
            # Wenn zuvor automatisch geladen wurde -> Zurück auf PV-Autarkie
            if active_dispatch == "forced_charge" or soc >= 95.0:
                cmd_text = f"AUTO: Zurück auf PV-Autarkie (Ladefenster beendet / SoC={soc:.0f}%)"
                storage.last_control_command = cmd_text
                storage.last_controlled_at = now
                storage.save(update_fields=["last_control_command", "last_controlled_at"])

                dispatch_res = dispatch_inverter_write_command(storage, "self_consumption", 0.0)
                logger.info("Storage %s: %s", storage.id, cmd_text)
                return {
                    "dispatched": True,
                    "action": "self_consumption",
                    "power_kw": 0.0,
                    "command": cmd_text,
                    "dispatch_result": dispatch_res,
                }

    # =========================================================================
    # MODUS 2: MANUELLES SOFORTLADEN (BOOST)
    # =========================================================================
    elif storage.control_mode == "forced_charge":
        target_power = float(storage.target_charge_power_kw or 3.0)
        if soc >= 98.0:
            # Akku ist voll -> Automatischer Reset auf PV-Autarkie
            storage.control_mode = "self_consumption"
            cmd_text = f"MANUAL: Sofortladen abgeschlossen (SoC={soc:.0f}%) -> Zurück auf PV-Autarkie"
            storage.last_control_command = cmd_text
            storage.last_controlled_at = now
            storage.save(update_fields=["control_mode", "last_control_command", "last_controlled_at"])

            dispatch_res = dispatch_inverter_write_command(storage, "self_consumption", 0.0)
            return {
                "dispatched": True,
                "action": "self_consumption",
                "power_kw": 0.0,
                "command": cmd_text,
                "dispatch_result": dispatch_res,
            }
        else:
            # Ladung aktiv halten
            dispatch_res = dispatch_inverter_write_command(storage, "forced_charge", target_power)
            return {
                "dispatched": True,
                "action": "forced_charge",
                "power_kw": target_power,
                "dispatch_result": dispatch_res,
            }

    return {"dispatched": False, "reason": "no_action_needed"}


def dispatch_all_storage_systems() -> dict:
    """
    Läuft zyklisch über alle aktiven Batteriespeicher im System.
    """
    storages = StorageSystem.objects.filter(active=True, ems_control_enabled=True)
    results = []
    now = timezone.now()

    for storage in storages:
        res = evaluate_and_dispatch_storage_system(storage, now=now)
        results.append({
            "storage_id": str(storage.id),
            "storage_name": storage.name,
            "result": res,
        })

    return {
        "dispatched_count": len([r for r in results if r["result"].get("dispatched")]),
        "total_evaluated": len(results),
        "results": results,
    }
