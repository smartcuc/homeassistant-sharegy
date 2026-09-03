"""
producer/services_sungrow_control.py

Bi-Direktionale Steuerung von Sungrow Wechselrichtern und SBR-Batteriespeichern
über die offizielle Sungrow iSolarCloud OpenAPI.

Unterstützt:
- forced_charge: Zwangsladung aus dem Stromnetz bei negativen / günstigen Börsenpreisen mit Soll-Leistung (kW)
- self_consumption: Rückkehr zur Standard-PV-Autarkie (Eigenverbrauchsoptimierung)
- forced_discharge: Forcierte Netzeinspeisung / Spitzenlastkappung
"""

import os
import logging
import requests
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from producer.models import StorageSystem
from devices.models import CloudDeviceIntegration

logger = logging.getLogger("producer.sungrow_control")

SUNGROW_APPKEY = getattr(settings, "SUNGROW_APPKEY", None) or os.getenv("SUNGROW_APPKEY") or "988713D7D057090474AEC9584CBA1AAD"
SUNGROW_APP_SECRET = getattr(settings, "SUNGROW_APP_SECRET", None) or os.getenv("SUNGROW_APP_SECRET") or "chh8ptt9n6xkchjr0yez6hxadxh58vc9"
SUNGROW_GATEWAY_URL = getattr(settings, "SUNGROW_GATEWAY_URL", "https://gateway.isolarcloud.eu")


def send_sungrow_cloud_control_command(storage: StorageSystem, action: str, power_kw: float, target_soc: float = None) -> dict:
    """
    Sendet einen aktiven Steuerbefehl an die Sungrow iSolarCloud OpenAPI.

    action: 'forced_charge' | 'self_consumption' | 'forced_discharge'
    power_kw: Gewünschte Lade-/Entladeleistung in kW (z. B. 5.0 kW)
    target_soc: Ziel-SoC in % (z. B. 95.0 %)
    """
    home = storage.home
    power_watts = int(power_kw * 1000)
    now = timezone.now()

    # 1. Sungrow Integration & Token für das Home ermitteln
    integration = None
    dev = getattr(storage, "primary_device", None) or getattr(storage, "soc_device", None)
    if dev:
        integration = CloudDeviceIntegration.objects.filter(
            device=dev,
            profile_id="sungrow_isolarcloud",
            is_active=True,
        ).first()

    if not integration and home:
        integration = CloudDeviceIntegration.objects.filter(
            device__home=home,
            profile_id="sungrow_isolarcloud",
            is_active=True,
        ).first()

    credentials = integration.credentials if integration else {}
    token = credentials.get("token") or credentials.get("access_token")
    ps_id = credentials.get("ps_id") or "default_ps"
    appkey = credentials.get("appkey") or SUNGROW_APPKEY

    # Betriebsmodus-Codes für Sungrow:
    # 0 = Self-Consumption (Eigenverbrauch / PV-Autarkie)
    # 1 = Forced Charging (Zwangsladung aus dem Netz)
    # 2 = Forced Discharging (Forcierte Entladung)
    # 3 = Backup / Standby
    mode_code = 1 if action == "forced_charge" else (0 if action == "self_consumption" else 2)

    result_payload = {
        "status": "success",
        "action": action,
        "mode_code": mode_code,
        "power_kw": float(power_kw),
        "power_w": power_watts,
        "storage_id": str(storage.id),
        "ps_id": ps_id,
        "timestamp": now.isoformat(),
        "source": "sungrow_openapi",
    }

    # Wenn ein echter OpenAPI Token vorhanden ist (kein reiner Test-Mock)
    if token and not token.startswith("sg_oauth_demo") and not token.startswith("sg_oauth_test"):
        try:
            headers = {
                "x-access-key": SUNGROW_APP_SECRET,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            # OpenAPI Endpunkt zur Sollwertvorgabe
            control_url = f"{SUNGROW_GATEWAY_URL}/openapi/platform/setDeviceRunParam"
            body = {
                "appkey": appkey,
                "ps_id": ps_id,
                "param_list": [
                    {"param_key": "ems_work_mode", "param_val": str(mode_code)},
                    {"param_key": "charge_power_limit", "param_val": str(power_watts)},
                ],
            }
            if target_soc is not None:
                body["param_list"].append({"param_key": "target_soc", "param_val": str(int(target_soc))})

            resp = requests.post(control_url, json=body, headers=headers, timeout=10)
            if resp.status_code == 200:
                resp_json = resp.json()
                result_payload["api_response"] = resp_json
                logger.info("Sungrow OpenAPI control command sent [%s]: %s", action, resp_json)
            else:
                logger.warning("Sungrow OpenAPI control status code %s: %s", resp.status_code, resp.text)
                result_payload["warning"] = f"HTTP {resp.status_code}"
        except Exception as e:
            logger.error("Sungrow OpenAPI control error: %s", e)
            result_payload["error"] = str(e)
    else:
        # Simulation / Sandbox Modus
        logger.info(
            "Sungrow OpenAPI simulation command executed for storage %s: %s (%s kW)",
            storage.name,
            action,
            power_kw,
        )
        result_payload["simulated"] = True

    # Cache aktualisieren für Sub-Sekunden Status im Dashboard
    cache.set(f"storage:{storage.id}:sungrow_mode", mode_code, timeout=86400)
    cache.set(f"storage:{storage.id}:sungrow_target_power_kw", float(power_kw), timeout=86400)
    cache.set(f"storage:{storage.id}:sungrow_last_command_ts", now.isoformat(), timeout=86400)

    return result_payload
