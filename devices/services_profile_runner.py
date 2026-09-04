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

from devices.models import Device, DeviceMetric, DeviceLatestMetric, CloudDeviceIntegration


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


def _clean_numeric_value(raw_val, target_unit="W"):
    """
    Konvertiert Zahlen oder formatierte Strings mit Einheiten wie '677.3 W', '0.68 kW', '3.5 kWh', '85 %'
    in saubere Floats mit automatischer Einheitenskalierung.
    """
    if raw_val is None:
        return None
    if isinstance(raw_val, (int, float)):
        return float(raw_val)

    s = str(raw_val).strip().replace(",", ".")
    if not s or s in ("-", "--", "null", "None", "N/A", "n/a"):
        return None

    lower_s = s.lower()
    factor = 1.0

    if target_unit == "W":
        if "kw" in lower_s:
            factor = 1000.0
            lower_s = lower_s.replace("kw", "").strip()
        elif "mw" in lower_s:
            factor = 1000000.0
            lower_s = lower_s.replace("mw", "").strip()
        elif "w" in lower_s:
            lower_s = lower_s.replace("w", "").strip()
    elif target_unit == "kWh":
        if "mwh" in lower_s:
            factor = 1000.0
            lower_s = lower_s.replace("mwh", "").strip()
        elif "wh" in lower_s and "kwh" not in lower_s:
            factor = 0.001
            lower_s = lower_s.replace("wh", "").strip()
        elif "kwh" in lower_s:
            lower_s = lower_s.replace("kwh", "").strip()
    elif target_unit == "%":
        lower_s = lower_s.replace("%", "").strip()

    import re
    match = re.search(r"[-+]?\d*\.?\d+", lower_s)
    if match:
        try:
            return float(match.group(0)) * factor
        except (ValueError, TypeError):
            return None
    return None


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
    elif profile_id == "deye_solarman":
        return {
            "dataList": [
                {"key": "APo_t1", "value": pv_kw * 1000},
                {"key": "TotalGridPower", "value": grid_kw * 1000},
                {"key": "TotalLoadPower", "value": load_kw * 1000},
                {"key": "B_P1", "value": battery_kw * 1000},
                {"key": "SOC", "value": round(random.uniform(70.0, 95.0), 1)},
            ]
        }
    elif profile_id == "huawei_fusionsolar":
        return {
            "data": [
                {
                    "dataItemMap": {
                        "inverter_power": pv_kw,
                        "grid_power": grid_kw,
                        "use_power": load_kw,
                        "battery_power": battery_kw,
                        "battery_soc": round(random.uniform(65.0, 92.0), 1),
                    }
                }
            ]
        }
    elif profile_id == "goodwe_sems":
        return {
            "data": {
                "kpi": {
                    "pac": pv_kw * 1000,
                    "grid_power": grid_kw * 1000,
                    "load_power": load_kw * 1000,
                    "battery_power": battery_kw * 1000,
                    "soc": round(random.uniform(60.0, 90.0), 1),
                }
            }
        }
    elif profile_id == "solis_cloud":
        return {
            "data": {
                "power": pv_kw,
                "gridPurchasedPower": grid_kw,
                "familyLoadPower": load_kw,
                "batteryPower": battery_kw,
                "batteryPercent": round(random.uniform(65.0, 95.0), 1),
            }
        }
    elif profile_id == "victron_vrm":
        return {
            "records": {
                "solar_yield": pv_kw * 1000,
                "grid_power": grid_kw * 1000,
                "consumption": load_kw * 1000,
                "battery_power": battery_kw * 1000,
                "soc": round(random.uniform(70.0, 95.0), 1),
            }
        }
    else:
        return {
            "pv_power": pv_kw * 1000,
            "grid_power": grid_kw * 1000,
            "load_power": load_kw * 1000,
            "battery_soc": 80.0,
        }


def _growatt_hash_password(password: str) -> str:
    """
    MD5-Hash mit 'c'-Ersetzung an ungeraden Positionen für 0-Nibbles (Growatt-Standard).
    Entspricht der Growatt Web/App Authentifizierung (PyPi_GrowattServer).
    """
    import hashlib
    password_md5 = hashlib.md5(str(password).encode("utf-8")).hexdigest()
    res = list(password_md5)
    for i in range(0, len(res), 2):
        if res[i] == "0":
            res[i] = "c"
    return "".join(res)


def _execute_growatt_query(base_url: str, credentials: dict) -> dict:
    """
    Robustes Growatt Cloud & OpenAPI Ingestion Modul:
    1. Pfad A: Token-basierter OpenAPI Zugriff (Growatt OpenAPI V1 / V4 via ShowDoc Spezifikation)
    2. Pfad B: Username + Passwort Session Login (ShineServer / ShinePhone App via PyPi_GrowattServer)
    """
    token = credentials.get("token") or credentials.get("api_key")
    plant_id = credentials.get("plant_id") or ""
    device_sn = credentials.get("device_sn") or credentials.get("sn") or ""
    username = credentials.get("user_account") or credentials.get("username") or credentials.get("userName")
    password = credentials.get("user_password") or credentials.get("password")

    raw_data = {"data": {}}
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Sharegy EMS GrowattConnector)",
    })

    # PFAD A: Offizielle Growatt OpenAPI (Token vorhanden)
    if token and not str(token).startswith("test_") and not str(token).startswith("mock_"):
        api_headers = {
            "token": str(token).strip(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        # 1. Falls keine plant_id bekannt ist, automatisch via /v1/plant/list ermitteln
        if not plant_id:
            try:
                plist_resp = session.get("https://openapi.growatt.com/v1/plant/list", headers={"token": token}, timeout=10)
                if plist_resp.status_code == 200:
                    p_json = plist_resp.json()
                    plants = p_json.get("data", {}).get("plants", []) if isinstance(p_json.get("data"), dict) else []
                    if plants and isinstance(plants, list):
                        plant_id = str(plants[0].get("plant_id") or plants[0].get("id") or "")
                        credentials["plant_id"] = plant_id
            except Exception as e:
                logger.warning("Growatt OpenAPI plant list discovery failed: %s", e)

        # 2. Geräte auflösen (falls device_sn noch nicht bekannt)
        if plant_id and not device_sn:
            try:
                dlist_resp = session.get(
                    "https://openapi.growatt.com/v1/device/list",
                    headers={"token": token},
                    params={"plant_id": plant_id},
                    timeout=10,
                )
                if dlist_resp.status_code == 200:
                    d_json = dlist_resp.json()
                    devices = d_json.get("data", {}).get("devices", []) if isinstance(d_json.get("data"), dict) else []
                    if devices and isinstance(devices, list):
                        device_sn = str(devices[0].get("device_sn") or devices[0].get("sn") or "")
                        credentials["device_sn"] = device_sn
            except Exception as e:
                logger.debug("Growatt device/list lookup failed: %s", e)

        # 3. Spezifische Inverter / Storage Last Data Endpunkte abfragen
        if device_sn:
            for endpoint in [
                "https://openapi.growatt.com/v1/device/inverter/inverter_last_data",
                "https://openapi.growatt.com/v1/device/tlx/tlx_last_data",
                "https://openapi.growatt.com/v1/device/mix/mix_last_data",
                "https://openapi.growatt.com/v1/device/storage/storage_last_data",
                "https://openapi.growatt.com/v1/device/noah/noah_last_data",
            ]:
                try:
                    dev_resp = session.get(endpoint, headers={"token": token}, params={"device_sn": device_sn, "inverter_sn": device_sn, "tlx_sn": device_sn, "mix_sn": device_sn, "storage_sn": device_sn}, timeout=8)
                    if dev_resp.status_code == 200:
                        d_json = dev_resp.json()
                        d_data = d_json.get("data")
                        if isinstance(d_data, dict) and d_data:
                            raw_data["data"].update(d_data)
                except Exception:
                    pass

            for dev_type in ["inverter", "storage", "min", "sph", "noah", "tlx", "mix"]:
                try:
                    q_resp = session.post(
                        "https://openapi.growatt.com/v4/new-api/queryLastData",
                        headers=api_headers,
                        data={"deviceType": dev_type, "deviceSn": device_sn},
                        timeout=8,
                    )
                    if q_resp.status_code == 200:
                        q_json = q_resp.json()
                        dev_data = q_json.get("data", {}).get(dev_type) or q_json.get("data", {})
                        if isinstance(dev_data, dict) and dev_data:
                            raw_data["data"].update(dev_data)
                            break
                except Exception:
                    pass

        # 4. V1 Plant Data & Overview abfragen
        if plant_id:
            try:
                p_resp = session.get(
                    "https://openapi.growatt.com/v1/plant/data",
                    headers={"token": token},
                    params={"plant_id": plant_id},
                    timeout=10,
                )
                if p_resp.status_code == 200 and p_resp.json().get("data"):
                    raw_data["data"].update(p_resp.json()["data"])
            except Exception as e:
                logger.warning("Growatt plant/data failed: %s", e)

            try:
                ov_resp = session.post(
                    "https://openapi.growatt.com/v1/plant/data/overview",
                    headers={"token": token, "Content-Type": "application/json"},
                    json={"plant_id": plant_id},
                    timeout=10,
                )
                if ov_resp.status_code == 200 and ov_resp.json().get("data"):
                    raw_data["data"].update(ov_resp.json()["data"])
            except Exception:
                pass

        if raw_data.get("data"):
            return raw_data

    # PFAD B: ShineServer / ShinePhone Web Login (Username & Passwort via PyPi_GrowattServer)
    if username and password:
        hashed_pw = _growatt_hash_password(str(password))
        server_hosts = [
            "https://server.growatt.com",
            "https://server-api.growatt.com",
            "https://openapi.growatt.com",
        ]
        
        logged_in = False
        active_host = server_hosts[0]
        user_id = None

        for host in server_hosts:
            login_url = f"{host}/newTwoLoginAPI.do"
            try:
                l_resp = session.post(login_url, data={"userName": username, "password": hashed_pw}, timeout=10)
                if l_resp.status_code == 200:
                    l_json = l_resp.json().get("back", {})
                    if l_json.get("success"):
                        logged_in = True
                        active_host = host
                        user_id = l_json.get("user", {}).get("id") or l_json.get("userId")
                        credentials["user_id"] = user_id
                        break
            except Exception as e:
                logger.debug("Growatt login attempt failed on host %s: %s", host, e)

        if logged_in and user_id:
            try:
                # 1. Plant List & Übersicht
                p_list_resp = session.get(f"{active_host}/PlantListAPI.do", params={"userId": user_id}, timeout=10)
                if p_list_resp.status_code == 200:
                    plants_info = p_list_resp.json().get("back", {})
                    if plants_info.get("totalData"):
                        raw_data["data"].update(plants_info["totalData"])
                    plant_arr = plants_info.get("data", [])
                    if plant_arr and isinstance(plant_arr, list):
                        first_plant = plant_arr[0]
                        if isinstance(first_plant, dict):
                            raw_data["data"].update(first_plant)
                        if not plant_id:
                            plant_id = str(first_plant.get("plantId") or first_plant.get("id") or "")
                            credentials["plant_id"] = plant_id

                # 2. Plant Detail / Overview / Inverter
                if plant_id:
                    # Inverter List
                    inv_resp = session.post(
                        f"{active_host}/newTwoPlantAPI.do",
                        params={"op": "getAllPlantListTwo"},
                        data={"plantId": plant_id, "language": "1"},
                        timeout=10,
                    )
                    if inv_resp.status_code == 200:
                        inv_json = inv_resp.json()
                        if isinstance(inv_json, dict):
                            raw_data["data"].update(inv_json)

                    # Plant Energy Detail
                    det_resp = session.post(
                        f"{active_host}/newPlantDetailAPI.do",
                        data={"plantId": plant_id},
                        timeout=10,
                    )
                    if det_resp.status_code == 200:
                        det_json = det_resp.json()
                        if isinstance(det_json, dict):
                            raw_data["data"].update(det_json)

                    # Storage / Battery Status (falls Hybrid oder Speicher)
                    stor_resp = session.post(
                        f"{active_host}/newStorageAPI.do",
                        params={"op": "getStorageTotalData"},
                        data={"plantId": plant_id},
                        timeout=10,
                    )
                    if stor_resp.status_code == 200:
                        stor_json = stor_resp.json()
                        if isinstance(stor_json, dict):
                            stor_data = stor_json.get("obj") or stor_json.get("back") or stor_json
                            if isinstance(stor_data, dict):
                                raw_data["data"].update(stor_data)

                return raw_data
            except Exception as e:
                logger.warning("Growatt Web Login data retrieval error: %s", e)
                if raw_data.get("data"):
                    return raw_data
                raise ValueError(f"Growatt Datenabfrage fehlgeschlagen: {e}")
        elif not raw_data.get("data"):
            raise ValueError("Growatt Login fehlgeschlagen: Bitte prüfe Benutzername und Passwort.")

    return raw_data


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
        or "test" in str(credentials.get("token", "")).lower()
        or getattr(settings, "STRIPE_SANDBOX_MODE", True) and not credentials.get("appkey") and not credentials.get("token") and not credentials.get("user_account")
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
    if auth_type == "sungrow_token" or profile_id == "sungrow_isolarcloud":
        appkey = credentials.get("appkey") or getattr(settings, "SUNGROW_APPKEY", "") or os.getenv("SUNGROW_APPKEY", "")
        app_secret = getattr(settings, "SUNGROW_APP_SECRET", "") or os.getenv("SUNGROW_APP_SECRET", "")
        token = credentials.get("token")
        ps_id = credentials.get("ps_id") or credentials.get("ps_ids") or ""
        is_oauth = credentials.get("auth_type") == "oauth2" or (token and not str(token).startswith("sg_oauth_"))

        if is_oauth and token:
            # Falls noch ungetauschter Code vorhanden
            if str(token).startswith("sg_oauth_"):
                auth_code = str(token).replace("sg_oauth_", "").strip()
                try:
                    redir_url = getattr(settings, "SUNGROW_REDIRECT_URL", None) or os.getenv("SUNGROW_REDIRECT_URL") or "https://sharegy.de/api/v1/integrations/sungrow/callback"
                    t_resp = requests.post(
                        f"{base_url.rstrip('/')}/openapi/apiManage/token",
                        json={
                            "appkey": appkey,
                            "code": auth_code,
                            "grant_type": "authorization_code",
                            "redirect_uri": redir_url,
                        },
                        headers={"x-access-key": app_secret, "Content-Type": "application/json"},
                        timeout=10,
                    )
                    if t_resp.status_code == 200 and t_resp.json().get("access_token"):
                        token = t_resp.json()["access_token"]
                        credentials["token"] = token
                        if t_resp.json().get("refresh_token"):
                            credentials["refresh_token"] = t_resp.json()["refresh_token"]
                except Exception as ex_err:
                    logger.warning("Auto token exchange failed: %s", ex_err)

            # 1. OAuth2 OpenAPI Modus
            if not ps_id or ps_id in ("default_ps", "12345", ""):
                try:
                    list_resp = requests.post(
                        f"{base_url.rstrip('/')}/openapi/platform/queryPowerStationList",
                        json={"appkey": appkey, "page": 1, "size": 20, "lang": "_de_DE"},
                        headers={
                            "x-access-key": app_secret,
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                        },
                        timeout=12,
                    )
                    if list_resp.status_code == 200:
                        list_data = list_resp.json().get("result_data", {})
                        stations = list_data.get("pageList", []) if isinstance(list_data, dict) else []
                        if stations:
                            ps_id = str(stations[0].get("ps_id") or stations[0].get("id"))
                            credentials["ps_id"] = ps_id
                            credentials["ps_name"] = stations[0].get("ps_name", "Sungrow PV-Anlage")
                except Exception as e:
                    logger.warning("Auto-fetch ps_id via OpenAPI failed: %s", e)

            MEASURE_POINTS = [
                "83033", "83067", "83052", "83106", "83051", "83549",
                "83129", "83252", "83238", "83104", "83111", "83112", "83326",
                "83328", "83329", "83330", "83334"
            ]
            raw_data = {"result_code": "1", "result_data": {}}

            try:
                rt_resp = requests.post(
                    f"{base_url.rstrip('/')}/openapi/platform/getPowerStationRealTimeData",
                    json={
                        "appkey": appkey,
                        "ps_id_list": [str(ps_id or "")],
                        "point_id_list": MEASURE_POINTS,
                        "is_get_point_dict": "1",
                    },
                    headers={
                        "x-access-key": app_secret,
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    timeout=12,
                )
                if rt_resp.status_code == 200:
                    rt_json = rt_resp.json()
                    point_dict = rt_json.get("result_data", {}).get("point_dict", {})
                    if point_dict:
                        logger.info("[SUNGROW_OPENAPI] Discovered Point Dictionary: %s", point_dict)
                    pts = rt_json.get("result_data", {}).get("device_point_list", [])
                    if pts:
                        p_data = {}
                        for item in pts:
                            if isinstance(item, dict):
                                if "point_id" in item and "point_value" in item:
                                    pid = str(item["point_id"])
                                    p_data[pid] = item["point_value"]
                                    p_data[f"p{pid}"] = item["point_value"]
                                else:
                                    for k, v in item.items():
                                        ks = str(k)
                                        p_data[ks] = v
                                        if not ks.startswith("p"):
                                            p_data[f"p{ks}"] = v

                        def _get_pt(*keys):
                            for k in keys:
                                for variant in [str(k), f"p{k}", f"P{k}"]:
                                    if variant in p_data and p_data[variant] is not None:
                                        try:
                                            return float(p_data[variant])
                                        except (ValueError, TypeError):
                                            pass
                            return None

                        pv = _get_pt("83033", "83067", "83329") or 0.0
                        load = _get_pt("83052", "83106", "83330") or 0.0
                        grid = _get_pt("83051", "83549", "83328") or 0.0
                        bat_pwr = _get_pt("83104", "83238", "83111", "83112", "83326") or 0.0

                        soc_raw = _get_pt("83129", "83252", "83334")
                        soc_val = None
                        if soc_raw is not None:
                            if 0.0 <= soc_raw <= 1.0:
                                soc_val = round(soc_raw * 100.0, 1)
                            else:
                                soc_val = round(soc_raw, 1)

                        if soc_val is not None and soc_val >= 98.0:
                            if bat_pwr < 0:
                                bat_pwr = 0.0
                        elif pv > (load + 30) and (soc_val is None or soc_val < 98.0) and abs(bat_pwr) > 10:
                            bat_pwr = -abs(bat_pwr)
                        elif pv < 20 and soc_val is not None and soc_val > 5.0 and load > 20:
                            if abs(bat_pwr) < 0.1 and abs(grid) < 60:
                                bat_pwr = load
                            else:
                                bat_pwr = abs(bat_pwr)

                        if bat_pwr < 0:
                            bat_charge = abs(bat_pwr)
                            true_excess = max(0.0, pv - load - bat_charge)
                            if grid < 0 and abs(abs(grid) - bat_charge) < 200:
                                grid = -true_excess
                            elif grid < 0 and abs(grid) > (true_excess + 100):
                                grid = -true_excess

                        raw_data["_direct_metrics"] = {
                            "pv_power_w": max(0.0, pv),
                            "load_power_w": max(0.0, load),
                            "grid_power_w": grid,
                            "battery_power_w": bat_pwr,
                            "battery_soc": soc_val,
                        }
            except Exception as e:
                logger.warning("getPowerStationRealTimeData query failed: %s", e)

            # Details abfragen als Ergänzung
            try:
                resp = requests.post(
                    f"{base_url.rstrip('/')}/openapi/platform/getPowerStationDetail",
                    json={"appkey": appkey, "ps_ids": str(ps_id or ""), "lang": "_de_DE"},
                    headers={
                        "x-access-key": app_secret,
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    timeout=12,
                )
                if resp.status_code == 200:
                    det_json = resp.json()
                    if det_json.get("result_code") in ("2", "000") and credentials.get("refresh_token"):
                        try:
                            ref_resp = requests.post(
                                f"{base_url.rstrip('/')}/openapi/apiManage/refreshToken",
                                json={"appkey": appkey, "refresh_token": credentials["refresh_token"]},
                                headers={"x-access-key": app_secret, "Content-Type": "application/json"},
                                timeout=10,
                            )
                            if ref_resp.status_code == 200 and ref_resp.json().get("access_token"):
                                token = ref_resp.json()["access_token"]
                                credentials["token"] = token
                        except Exception as ref_err:
                            logger.warning("Token refresh error: %s", ref_err)

                    if det_json.get("result_data", {}).get("data_list"):
                        d_list = det_json["result_data"]["data_list"]
                        if isinstance(d_list, list) and d_list:
                            raw_data["result_data"].update(d_list[0])
            except Exception as e:
                logger.warning("getPowerStationDetail query failed: %s", e)
            
            live_metrics = _parse_metrics_from_payload(profile, raw_data)
            if raw_data.get("_direct_metrics"):
                for k, v in raw_data["_direct_metrics"].items():
                    if v is not None:
                        live_metrics[k] = v
            return {
                "status": "success",
                "message": f"Live-Verbindung zu {profile.get('name')} erfolgreich!",
                "live_metrics": live_metrics,
                "raw_sample": raw_data,
                "simulated": False,
            }

        else:
            # 2. Legacy / Password Login Modus
            if not token:
                token_info = _execute_sungrow_login(
                    base_url=base_url,
                    appkey=appkey,
                    account=credentials.get("user_account"),
                    password=credentials.get("user_password"),
                )
                token = token_info["token"]
                credentials["token"] = token
                credentials["user_id"] = token_info["user_id"]

            headers = {
                "Content-Type": "application/json",
                "sys_code": "901",
                "token": token,
            }
            body = {
                "appkey": appkey,
                "ps_id": str(ps_id or ""),
            }
            resp = requests.post(
                f"{base_url.rstrip('/')}/v1/powerStationService/getPowerStationDetail",
                headers=headers,
                json=body,
                timeout=12,
            )
            raw_data = resp.json() if resp.status_code == 200 else {}

    elif profile_id == "growatt_server":
        raw_data = _execute_growatt_query(base_url, credentials)

    else:
        # Standard GET/POST
        req_cfg = profile["requests"]["telemetry"]
        url = f"{base_url.rstrip('/')}{_render_template(req_cfg['endpoint'], credentials)}"
        headers = _render_template(req_cfg.get("headers", {}), credentials)
        params = _render_template(req_cfg.get("params", {}), credentials)
        body = _render_template(req_cfg.get("body", {}), credentials)
        method = str(req_cfg.get("method", "GET")).upper()

        if method == "POST":
            content_type = str(headers.get("Content-Type", "")).lower()
            if "application/json" in content_type:
                resp = requests.post(url, headers=headers, json=body, timeout=12)
            else:
                resp = requests.post(url, headers=headers, data=body, timeout=12)
        else:
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


def _flatten_payload_dict(payload) -> dict:
    """
    Sammelt alle Key-Value-Paare aus einem verschachtelten JSON-Objekt,
    inklusive Listen von Geräten (z.B. obj, deviceList, data, plants, invList, storageList),
    damit Metriken wie 'pac', 'currentPower', 'soc', 'eToday' immer gefunden werden.
    """
    flat = {}
    if not isinstance(payload, (dict, list)):
        return flat

    def _walk(item):
        if isinstance(item, dict):
            for k, v in item.items():
                if isinstance(v, (int, float, str, bool)) or v is None:
                    if k not in flat or flat[k] in (None, 0, 0.0, "0", "0 W", "", "0.0"):
                        flat[k] = v
                elif isinstance(v, (dict, list)):
                    _walk(v)
        elif isinstance(item, list):
            for elem in item:
                _walk(elem)

    _walk(payload)
    return flat


def _parse_metrics_from_payload(profile: dict, raw_payload: dict) -> dict:
    """
    Wendet das metrics_mapping des Profils auf die Rohdaten an und ergänzt
    intelligente Multi-Key Fallbacks mit automatischer Einheitenbereinigung (z. B. für Growatt, Sungrow etc.).
    """
    mapping = profile.get("metrics_mapping", {})
    extracted = {}

    # Vollständiger Fallback-Pool inklusive aller verschachtelten Listen & Dictionaries
    data_dict = _flatten_payload_dict(raw_payload)

    for metric_name, rule in mapping.items():
        jsonpath = rule.get("jsonpath")
        scale = float(rule.get("scale", 1.0))
        fallback = rule.get("fallback")
        transform = rule.get("transform")
        min_val = rule.get("min")
        max_val = rule.get("max")
        target_unit = "kWh" if "kwh" in metric_name else ("%" if "soc" in metric_name else "W")

        raw_val = extract_jsonpath(raw_payload, jsonpath, fallback=None)
        if raw_val is not None:
            raw_val = _clean_numeric_value(raw_val, target_unit=target_unit)

        # Intelligente Multi-Key Fallbacks falls JSONPath keinen Treffer liefert
        if raw_val is None:
            if metric_name == "pv_power_w":
                for k in ["currentPower", "current_power", "pac", "ppv", "pactouser", "nominalPower", "invPac", "power", "pacToUserTotal", "pv_power", "ppv1", "ppv2", "pPv1", "pPv2"]:
                    if k in data_dict and data_dict[k] is not None:
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="W")
                        if clean_v is not None:
                            raw_val = clean_v
                            break
            elif metric_name == "battery_soc":
                for k in ["soc", "batterySoc", "battery_soc", "batteryPercent", "chargeLevel", "capacity"]:
                    if k in data_dict and data_dict[k] is not None:
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="%")
                        if clean_v is not None:
                            raw_val = clean_v
                            break
            elif metric_name == "battery_power_w":
                for k in ["pdisCharge", "pcharge", "pdisCharge1", "pcharge1", "battery_power", "pactostorage", "pstorage"]:
                    if k in data_dict and data_dict[k] is not None:
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="W")
                        if clean_v is not None:
                            raw_val = clean_v
                            break
            elif metric_name == "grid_power_w":
                for k in ["pgrid", "pactogrid", "grid_power", "gridPower", "toGridPower"]:
                    if k in data_dict and data_dict[k] is not None:
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="W")
                        if clean_v is not None:
                            raw_val = clean_v
                            break
            elif metric_name == "load_power_w":
                for k in ["pload", "use_power", "familyLoadPower", "load_power", "loadPower", "useEnergy"]:
                    if k in data_dict and data_dict[k] is not None:
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="W")
                        if clean_v is not None:
                            raw_val = clean_v
                            break
            elif metric_name == "daily_generation_kwh":
                for k in ["eToday", "etoday", "todayEnergy", "e_today", "eTodayTotal", "eAcChargeToday"]:
                    if k in data_dict and data_dict[k] is not None:
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="kWh")
                        if clean_v is not None:
                            raw_val = clean_v
                            break

        if raw_val is None:
            raw_val = fallback

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
            val = float(metrics["pv_power_w"])
            DeviceMetric.objects.create(
                device=device,
                metric_key="power",
                unit="W",
                value=val,
                timestamp=now,
            )
            DeviceLatestMetric.objects.update_or_create(
                device=device,
                metric_key="power",
                defaults={"value": val, "timestamp": now},
            )
            try:
                cache.set(f"device:{device.id}:latest_power", val, timeout=3600)
                cache.set(f"device:{device.id}:pv_power", val, timeout=3600)
            except Exception as e:
                logger.warning("Cache write failed for device %s: %s", device.id, e)

        # 2. Battery SoC & Power
        has_battery = False
        if "battery_soc" in metrics and metrics["battery_soc"] is not None:
            has_battery = True
            soc_val = float(metrics["battery_soc"])
            DeviceMetric.objects.create(
                device=device,
                metric_key="battery_soc",
                unit="%",
                value=soc_val,
                timestamp=now,
            )
            DeviceLatestMetric.objects.update_or_create(
                device=device,
                metric_key="battery_soc",
                defaults={"value": soc_val, "timestamp": now},
            )
            try:
                cache.set(f"device:{device.id}:battery_soc", soc_val, timeout=3600)
                cache.set(f"device:{device.id}:latest_soc", soc_val, timeout=3600)
            except Exception as e:
                logger.warning("Cache write failed for battery_soc: %s", e)

        if "battery_power_w" in metrics and metrics["battery_power_w"] is not None:
            has_battery = True
            bat_pwr = float(metrics["battery_power_w"])
            DeviceMetric.objects.create(
                device=device,
                metric_key="battery_power",
                unit="W",
                value=bat_pwr,
                timestamp=now,
            )
            DeviceLatestMetric.objects.update_or_create(
                device=device,
                metric_key="battery_power",
                defaults={"value": bat_pwr, "timestamp": now},
            )
            try:
                cache.set(f"device:{device.id}:battery_power", bat_pwr, timeout=3600)
            except Exception as e:
                logger.warning("Cache write failed for battery_power: %s", e)

        # Automatische Verknüpfung / Anlegen von DeviceConfig & StorageSystem
        from devices.models import DeviceConfig, DeviceRole, MetricDefinition
        try:
            role_key = "both" if has_battery else "producer"
            target_role = DeviceRole.objects.filter(key=role_key).first() or DeviceRole.objects.filter(key="producer").first()
            p_metric = MetricDefinition.objects.filter(key="power").first()
            dev_cfg, _ = DeviceConfig.objects.get_or_create(
                device=device,
                defaults={
                    "home": device.home,
                    "name": credentials.get("ps_name") or "Sungrow Hybrid-Anlage",
                    "role": target_role,
                    "metric_definition": p_metric,
                }
            )
            if not dev_cfg.role:
                dev_cfg.role = target_role
                dev_cfg.save(update_fields=["role"])
        except Exception as cfg_err:
            logger.warning("Could not set DeviceConfig: %s", cfg_err)

        if has_battery and device.home:
            try:
                from producer.models import StorageSystem
                desired_cap = float(credentials.get("battery_capacity_kwh") or 22.5)
                storages = list(StorageSystem.objects.filter(home=device.home))
                if not storages:
                    st = StorageSystem.objects.create(
                        home=device.home,
                        name=f"{credentials.get('ps_name') or 'Sungrow'} Speicher",
                        primary_device=device,
                        soc_device=device,
                        power_device=device,
                        soc_metric_key="battery_soc",
                        power_metric_key="battery_power",
                        capacity_kwh=desired_cap,
                        max_charge_power_kw=10.0,
                        max_discharge_power_kw=10.0,
                        is_auto_detected=True,
                    )
                else:
                    for st in storages:
                        # Falls dieser Speicher noch kein Gerät hat oder bereits Sungrow zugeordnet ist
                        if not st.soc_device or st.soc_device == device or "sungrow" in st.name.lower():
                            st.primary_device = device
                            st.soc_device = device
                            st.power_device = device
                            st.soc_metric_key = "battery_soc"
                            st.power_metric_key = "battery_power"
                            if float(st.capacity_kwh) in (9.6, 10.0):
                                st.capacity_kwh = desired_cap
                            st.save()
            except Exception as st_err:
                logger.warning("Could not auto-link StorageSystem: %s", st_err)



        # 3. Load Power & Grid Power
        if "load_power_w" in metrics and metrics["load_power_w"] is not None:
            load_val = float(metrics["load_power_w"])
            DeviceMetric.objects.create(
                device=device,
                metric_key="load_power",
                unit="W",
                value=load_val,
                timestamp=now,
            )
            DeviceLatestMetric.objects.update_or_create(
                device=device,
                metric_key="load_power",
                defaults={"value": load_val, "timestamp": now},
            )
            try:
                cache.set(f"device:{device.id}:load_power", load_val, timeout=3600)
            except Exception as e:
                logger.warning("Cache write failed for load_power: %s", e)

        if "grid_power_w" in metrics and metrics["grid_power_w"] is not None:
            grid_val = float(metrics["grid_power_w"])
            DeviceMetric.objects.create(
                device=device,
                metric_key="grid_power",
                unit="W",
                value=grid_val,
                timestamp=now,
            )
            DeviceLatestMetric.objects.update_or_create(
                device=device,
                metric_key="grid_power",
                defaults={"value": grid_val, "timestamp": now},
            )
            try:
                cache.set(f"device:{device.id}:grid_power", grid_val, timeout=3600)
            except Exception as e:
                logger.warning("Cache write failed for grid_power: %s", e)


        # Status aktualisieren
        integration.last_polled_at = now
        integration.last_status = CloudDeviceIntegration.STATUS_OK
        integration.last_error_message = ""
        integration.save(update_fields=["last_polled_at", "last_status", "last_error_message", "updated_at"])

        # Gerät als aktiv & online markieren (für device_health und UI-Status)
        device.last_seen = now
        device.active = True
        device.save(update_fields=["last_seen", "active"])


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
