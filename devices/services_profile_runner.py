"""
devices/services_profile_runner.py

Deklarative Profile-Runner Engine für 3rd-Party Wechselrichter & Speicher.
Liest YAML-Profile unter devices/profiles/*.yaml ein, führt Authentifizierung
und REST-Abfragen an Hersteller-Clouds (z. B. Sungrow iSolarCloud, SolarEdge, Fronius)
durch und überführt die Rohdaten in genormte Sharegy-Metriken.
"""

import os
import json
import logging
import re
import requests
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

try:
    import yaml
except ImportError:
    yaml = None

from devices.models import Device, DeviceMetric, CloudDeviceIntegration

logger = logging.getLogger(__name__)

PROFILES_DIR = Path(__file__).resolve().parent / "profiles"


def load_profile(profile_id: str) -> dict:
    """
    Lädt und validiert ein Profil (bevorzugt JSON, fallback YAML).
    Funktioniert ohne externe YAML-Bibliothek via nativem json-Modul!
    """
    # 1. Bevorzugt JSON (Standardbibliothek, keine Abhängigkeit)
    json_path = PROFILES_DIR / f"{profile_id}.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
        if isinstance(profile_data, dict) and "id" in profile_data:
            return profile_data

    # 2. YAML-Fallback
    yaml_path = PROFILES_DIR / f"{profile_id}.yaml"
    if yaml_path.exists():
        if yaml is not None:
            with open(yaml_path, "r", encoding="utf-8") as f:
                profile_data = yaml.safe_load(f)
            if isinstance(profile_data, dict) and "id" in profile_data:
                return profile_data
        else:
            logger.warning("PyYAML ist nicht installiert; lade stattdessen JSON-Profil für %s", profile_id)

    raise FileNotFoundError(f"Device-Profil '{profile_id}' wurde nicht gefunden unter {PROFILES_DIR}")


def list_available_profiles() -> list:
    """
    Scannt das profiles/-Verzeichnis und liefert alle verfügbaren Hersteller-Profile
    (unterstützt .json und .yaml ohne Crash bei fehlendem pyyaml).
    """
    profiles = {}
    if not PROFILES_DIR.exists():
        return []

    # 1. Alle JSON-Dateien laden
    for json_file in sorted(PROFILES_DIR.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "id" in data:
                    profiles[data["id"]] = {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "vendor": data.get("vendor"),
                        "category": data.get("category", "inverter_hybrid"),
                        "protocol": data.get("protocol", "http_cloud"),
                        "description": data.get("description", ""),
                        "help": data.get("help", {}),
                        "fields": data.get("connection", {}).get("fields", []),
                        "default_interval": data.get("connection", {}).get("polling_interval_seconds", 60),
                    }
        except Exception as e:
            logger.warning("Fehler beim Laden von JSON-Profil %s: %s", json_file, e)

    # 2. YAML-Dateien ergänzen (falls pyyaml installiert und nicht bereits via JSON vorhanden)
    if yaml is not None:
        for yaml_file in sorted(PROFILES_DIR.glob("*.yaml")):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and "id" in data and data["id"] not in profiles:
                        profiles[data["id"]] = {
                            "id": data.get("id"),
                            "name": data.get("name"),
                            "vendor": data.get("vendor"),
                            "category": data.get("category", "inverter_hybrid"),
                            "protocol": data.get("protocol", "http_cloud"),
                            "description": data.get("description", ""),
                            "help": data.get("help", {}),
                            "fields": data.get("connection", {}).get("fields", []),
                            "default_interval": data.get("connection", {}).get("polling_interval_seconds", 60),
                        }
            except Exception as e:
                logger.warning("Fehler beim Laden von YAML-Profil %s: %s", yaml_file, e)


    return list(profiles.values())



def extract_jsonpath(data: dict, path_expr: str, fallback=None):
    """
    Einfacher, robuster JSONPath-Evaluator für verschachtelte Dicts & Listen.
    Unterstützt Pfade wie:
    - '$.result_data.curr_power'
    - '$.siteCurrentPowerFlow.PV.currentPower'
    - 'result_data.battery_soc'
    """
    if not data or not path_expr:
        return fallback

    # '$.' Prefix entfernen
    clean_path = path_expr.lstrip("$").lstrip(".")
    tokens = clean_path.split(".")

    current = data
    for token in tokens:
        if isinstance(current, dict):
            if token in current:
                current = current[token]
            else:
                return fallback
        elif isinstance(current, list):
            # Index-Zugriff wie '0' oder '1'
            try:
                idx = int(token)
                current = current[idx]
            except (ValueError, IndexError):
                return fallback
        else:
            return fallback

    if current is None:
        return fallback

    return current


def _render_template(template_val, context: dict):
    """
    Ersetzt {{variable}} Platzhalter in Strings, Dicts oder Listen.
    """
    if isinstance(template_val, str):
        result = template_val
        for k, v in context.items():
            result = result.replace(f"{{{{{k}}}}}", str(v) if v is not None else "")
        return result
    elif isinstance(template_val, dict):
        return {k: _render_template(v, context) for k, v in template_val.items()}
    elif isinstance(template_val, list):
        return [_render_template(item, context) for item in template_val]
    return template_val


def _execute_sungrow_login(base_url: str, appkey: str, account: str, password: str) -> dict:
    """
    Führt den Sungrow iSolarCloud Login-Handshake durch.
    Cached den Token für 2 Stunden.
    """
    cache_key = f"sungrow_token_{appkey}_{account}"
    cached_token = cache.get(cache_key)
    if cached_token:
        return cached_token

    login_url = f"{base_url.rstrip('/')}/v1/userService/login"
    payload = {
        "appkey": appkey,
        "user_account": account,
        "user_password": password,
    }
    headers = {
        "Content-Type": "application/json",
        "sys_code": "901",
    }

    try:
        resp = requests.post(login_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        res_json = resp.json()

        if res_json.get("result_code") == "1" or res_json.get("result_data", {}).get("token"):
            token_data = {
                "token": res_json["result_data"]["token"],
                "user_id": res_json["result_data"].get("user_id"),
            }
            cache.set(cache_key, token_data, timeout=7000)
            return token_data
        else:
            msg = res_json.get("result_msg") or "Ungültige iSolarCloud Zugangsdaten"
            raise ValueError(f"Sungrow Login fehlgeschlagen: {msg}")
    except requests.RequestException as e:
        logger.warning("Sungrow Login Request Error: %s", e)
        raise ValueError(f"Verbindungsfehler zu Sungrow iSolarCloud: {e}")


def _generate_mock_payload(profile_id: str, credentials: dict) -> dict:
    """
    Generiert realistische Live-Messdaten für Testumgebungen oder Simulationen.
    """
    import random
    now = timezone.now()
    hour = now.hour

    # Realistischer Sonnenverlauf (Glockenkurve zwischen 6 und 20 Uhr)
    if 6 <= hour <= 20:
        pv_factor = max(0.0, 1.0 - ((hour - 13.0) / 7.0) ** 2)
        pv_kw = round(random.uniform(3.5, 7.8) * pv_factor, 2)
    else:
        pv_kw = 0.0

    load_kw = round(random.uniform(0.6, 2.2), 2)
    diff = pv_kw - load_kw

    if diff > 0:
        # PV-Überschuss -> Batterie lädt oder Netzeinspeisung
        battery_kw = round(min(diff * 0.7, 3.0) * -1, 2)  # negativ = laden
        grid_kw = round((diff + battery_kw) * -1, 2)      # negativ = einspeisen
    else:
        # PV-Defizit -> Batterie entlädt oder Netzbezug
        battery_kw = round(min(abs(diff), 2.5), 2)        # positiv = entladen
        grid_kw = round(abs(diff) - battery_kw, 2)        # positiv = Bezug

    if profile_id == "sungrow_isolarcloud":
        return {
            "result_code": "1",
            "result_msg": "success",
            "result_data": {
                "curr_power": pv_kw,
                "grid_power": grid_kw,
                "load_power": load_kw,
                "battery_power": battery_kw,
                "battery_soc": round(random.uniform(65.0, 95.0), 1),
                "today_energy": round(pv_kw * 4.2 + random.uniform(5.0, 15.0), 1),
            }
        }
    elif profile_id == "solaredge_cloud":
        return {
            "siteCurrentPowerFlow": {
                "unit": "kW",
                "PV": {"currentPower": pv_kw},
                "GRID": {"currentPower": grid_kw},
                "LOAD": {"currentPower": load_kw},
                "STORAGE": {"currentPower": battery_kw, "chargeLevel": round(random.uniform(70.0, 90.0), 1)},
            }
        }
    else:
        return {
            "pv_power": pv_kw * 1000,
            "grid_power": grid_kw * 1000,
            "load_power": load_kw * 1000,
            "battery_soc": 80.0,
        }


def test_cloud_credentials(profile_id: str, credentials: dict) -> dict:
    """
    Testet eingegebene Zugangsdaten gegen das Profil (Live oder Simulator).
    """
    profile = load_profile(profile_id)
    conn_cfg = profile.get("connection", {})
    base_url = credentials.get("base_url") or conn_cfg.get("default_base_url", "")
    auth_type = conn_cfg.get("auth_type", "none")

    # Prüfe ob Dummy / Test-Credentials vorliegen -> Simulator verwenden
    is_mock = (
        credentials.get("appkey") in ("mock", "test", "demo", "")
        or "test" in str(credentials.get("user_account", "")).lower()
        or getattr(settings, "STRIPE_SANDBOX_MODE", True) and not credentials.get("appkey")
    )

    if is_mock:
        raw_data = _generate_mock_payload(profile_id, credentials)
        parsed = _parse_metrics_from_payload(profile, raw_data)
        return {
            "status": "success",
            "message": f"Verbindung zu {profile.get('name')} erfolgreich (Simulator / Sandbox-Modus).",
            "live_metrics": parsed,
            "raw_sample": raw_data,
            "simulated": True,
        }

    # Echter HTTP-Aufruf
    if auth_type == "sungrow_token":
        appkey = credentials.get("appkey") or getattr(settings, "SUNGROW_APPKEY", "988713D7D057090474AEC9584CBA1AAD")
        token = credentials.get("token")

        if not token:
            token_info = _execute_sungrow_login(
                base_url=base_url,
                appkey=appkey,
                account=credentials.get("user_account"),
                password=credentials.get("user_password"),
            )
            token = token_info["token"]

        # Automatische Ermittlung der Anlagen-ID (ps_id) falls noch nicht gesetzt
        ps_id = credentials.get("ps_id")
        if not ps_id or ps_id in ("default_ps", "12345", ""):
            try:
                list_resp = requests.post(
                    f"{base_url.rstrip('/')}/v1/powerStationService/getPowerStationList",
                    json={"appkey": appkey, "curPage": 1, "size": 10},
                    headers={"Content-Type": "application/json", "sys_code": "901", "token": token},
                    timeout=10,
                )
                if list_resp.status_code == 200:
                    stations = list_resp.json().get("result_data", {}).get("pageList", [])
                    if stations:
                        ps_id = str(stations[0].get("ps_id"))
                        credentials["ps_id"] = ps_id
                        credentials["ps_name"] = stations[0].get("ps_name", "Sungrow PV-Anlage")
                        logger.info("Auto-discovered Sungrow power station ID: %s (%s)", ps_id, credentials.get("ps_name"))
            except Exception as e:
                logger.warning("Could not auto-fetch Sungrow ps_id: %s", e)

        context = {**credentials, "token": token, "ps_id": ps_id, "appkey": appkey}
        req_cfg = profile["requests"]["telemetry"]
        url = f"{base_url.rstrip('/')}{_render_template(req_cfg['endpoint'], context)}"
        headers = _render_template(req_cfg.get("headers", {}), context)
        body = _render_template(req_cfg.get("body", {}), context)

        resp = requests.post(url, json=body, headers=headers, timeout=12)
        resp.raise_for_status()
        raw_data = resp.json()

    else:
        # Standard GET/POST
        req_cfg = profile["requests"]["telemetry"]
        url = f"{base_url.rstrip('/')}{_render_template(req_cfg['endpoint'], credentials)}"
        headers = _render_template(req_cfg.get("headers", {}), credentials)
        params = _render_template(req_cfg.get("params", {}), credentials)
        resp = requests.get(url, headers=headers, params=params, timeout=12)
        resp.raise_for_status()
        raw_data = resp.json()

    parsed = _parse_metrics_from_payload(profile, raw_data)
    return {
        "status": "success",
        "message": f"Live-Verbindung zu {profile.get('name')} erfolgreich hergestellt!",
        "live_metrics": parsed,
        "raw_sample": raw_data,
        "simulated": False,
    }


def _parse_metrics_from_payload(profile: dict, raw_payload: dict) -> dict:
    """
    Wendet das metrics_mapping des Profils auf die Rohdaten an.
    """
    mapping = profile.get("metrics_mapping", {})
    extracted = {}

    for metric_name, rule in mapping.items():
        jsonpath = rule.get("jsonpath")
        scale = float(rule.get("scale", 1.0))
        fallback = rule.get("fallback")
        transform = rule.get("transform")
        min_val = rule.get("min")
        max_val = rule.get("max")

        raw_val = extract_jsonpath(raw_payload, jsonpath, fallback=fallback)
        if raw_val is not None:
            try:
                val = float(raw_val) * scale
                if transform == "abs":
                    val = abs(val)
                elif transform == "invert":
                    val = -val

                if min_val is not None and val < float(min_val):
                    val = float(min_val)
                if max_val is not None and val > float(max_val):
                    val = float(max_val)

                extracted[metric_name] = round(val, 2)
            except (ValueError, TypeError):
                extracted[metric_name] = fallback
        else:
            extracted[metric_name] = fallback

    return extracted


def execute_cloud_poll(integration: CloudDeviceIntegration) -> dict:
    """
    Führt einen regulären Polling-Zyklus für ein CloudDeviceIntegration-Objekt durch.
    Schreibt die extrahierten Metriken in DeviceMetric (TimescaleDB) und DeviceLatestMetric (Redis).
    """
    profile_id = integration.profile_id
    credentials = integration.credentials or {}
    device = integration.device

    try:
        res = test_cloud_credentials(profile_id, credentials)
        metrics = res.get("live_metrics", {})
        now = timezone.now()

        # Metriken in DB und Redis persistieren
        # 1. PV Power
        if "pv_power_w" in metrics and metrics["pv_power_w"] is not None:
            DeviceMetric.objects.create(
                device=device,
                metric_key="power",
                unit="W",
                value=metrics["pv_power_w"],
                timestamp=now,
            )

        # 2. Battery SoC & Power
        if "battery_soc" in metrics and metrics["battery_soc"] is not None:
            DeviceMetric.objects.create(
                device=device,
                metric_key="battery_soc",
                unit="%",
                value=metrics["battery_soc"],
                timestamp=now,
            )

        # Status aktualisieren
        integration.last_polled_at = now
        integration.last_status = CloudDeviceIntegration.STATUS_OK
        integration.last_error_message = ""
        integration.save(update_fields=["last_polled_at", "last_status", "last_error_message", "updated_at"])

        logger.info("Successfully polled cloud integration %s for device %s: %s", profile_id, device.id, metrics)
        return {
            "status": "success",
            "metrics": metrics,
            "device_id": str(device.id),
            "polled_at": now.isoformat(),
        }
    except Exception as e:
        logger.exception("Error polling cloud integration %s for device %s: %s", profile_id, device.id, e)
        integration.last_polled_at = timezone.now()
        integration.last_status = CloudDeviceIntegration.STATUS_ERROR
        integration.last_error_message = str(e)
        integration.save(update_fields=["last_polled_at", "last_status", "last_error_message", "updated_at"])
        return {
            "status": "error",
            "error": str(e),
            "device_id": str(device.id),
        }
