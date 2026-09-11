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

    try:
        from energy.services.ems_settings import get_manufacturer_polling_interval
    except Exception:
        get_manufacturer_polling_interval = None

    # 1. Alle JSON-Dateien laden
    for json_file in sorted(PROFILES_DIR.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "id" in data:
                    prof_id = data["id"]
                    yaml_interval = data.get("connection", {}).get("polling_interval_seconds", 60)
                    default_int = (
                        get_manufacturer_polling_interval(prof_id, default=yaml_interval)
                        if get_manufacturer_polling_interval
                        else yaml_interval
                    )
                    profiles[prof_id] = {
                        "id": prof_id,
                        "name": data.get("name"),
                        "vendor": data.get("vendor"),
                        "category": data.get("category", "inverter_hybrid"),
                        "protocol": data.get("protocol", "http_cloud"),
                        "description": data.get("description", ""),
                        "help": data.get("help", {}),
                        "fields": data.get("connection", {}).get("fields", []),
                        "default_interval": default_int,
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
                        prof_id = data["id"]
                        yaml_interval = data.get("connection", {}).get("polling_interval_seconds", 60)
                        default_int = (
                            get_manufacturer_polling_interval(prof_id, default=yaml_interval)
                            if get_manufacturer_polling_interval
                            else yaml_interval
                        )
                        profiles[prof_id] = {
                            "id": prof_id,
                            "name": data.get("name"),
                            "vendor": data.get("vendor"),
                            "category": data.get("category", "inverter_hybrid"),
                            "protocol": data.get("protocol", "http_cloud"),
                            "description": data.get("description", ""),
                            "help": data.get("help", {}),
                            "fields": data.get("connection", {}).get("fields", []),
                            "default_interval": default_int,
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
    - Automatische Auflösung von Listen wie result_data.data_list[0] oder result_data.pageList[0]
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
            elif "data_list" in current and isinstance(current["data_list"], list) and current["data_list"]:
                first_item = current["data_list"][0]
                if isinstance(first_item, dict) and token in first_item:
                    current = first_item[token]
                else:
                    return fallback
            elif "pageList" in current and isinstance(current["pageList"], list) and current["pageList"]:
                first_item = current["pageList"][0]
                if isinstance(first_item, dict) and token in first_item:
                    current = first_item[token]
                else:
                    return fallback
            elif "data" in current and isinstance(current["data"], list) and current["data"]:
                first_item = current["data"][0]
                if isinstance(first_item, dict) and token in first_item:
                    current = first_item[token]
                else:
                    return fallback
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

    # PFAD B: ShineServer / ShinePhone Web Login (Home Assistant / PyPi_GrowattServer kompatibel)
    if username and password:
        hashed_pw = _growatt_hash_password(str(password))
        server_hosts = [
            "https://server.growatt.com",
            "https://server-api.growatt.com",
            "https://server-us.growatt.com",
            "https://openapi.growatt.com",
        ]
        
        logged_in = False
        active_host = server_hosts[0]
        user_id = None

        for host in server_hosts:
            for pw_candidate in [hashed_pw, str(password)]:
                try:
                    l_resp = session.post(
                        f"{host}/newTwoLoginAPI.do",
                        data={"userName": username, "password": pw_candidate},
                        timeout=10,
                    )
                    if l_resp.status_code == 200:
                        l_body = l_resp.json()
                        l_back = l_body.get("back", {}) if isinstance(l_body.get("back"), dict) else l_body
                        if l_back.get("success") or l_body.get("result") == 1 or l_body.get("success"):
                            logged_in = True
                            active_host = host
                            user_id = (
                                l_back.get("user", {}).get("id")
                                or l_back.get("userId")
                                or l_back.get("user", {}).get("userId")
                                or l_body.get("obj", {}).get("userId")
                                or l_body.get("obj", {}).get("id")
                                or l_body.get("data", {}).get("userId")
                                or l_body.get("data", {}).get("id")
                                or l_body.get("userId")
                            )
                            credentials["user_id"] = user_id
                            break
                except Exception as e:
                    logger.debug("Growatt login attempt failed on host %s: %s", host, e)

                try:
                    form_resp = session.post(
                        f"{host}/login",
                        data={"account": username, "password": pw_candidate, "validateCode": ""},
                        timeout=10,
                    )
                    if form_resp.status_code == 200:
                        try:
                            f_body = form_resp.json()
                            if f_body.get("result") == 1 or f_body.get("success"):
                                logged_in = True
                                active_host = host
                                user_id = f_body.get("obj", {}).get("userId") or user_id
                                break
                        except Exception:
                            if "index" in form_resp.url or "main" in form_resp.url or session.cookies.get("JSESSIONID"):
                                logged_in = True
                                active_host = host
                                break
                except Exception as e:
                    logger.debug("Growatt /login endpoint failed on host %s: %s", host, e)

                if logged_in:
                    break
            if logged_in:
                break

        if logged_in:
            try:
                today_str = timezone.now().strftime("%Y-%m-%d")

                # 1. Plant List & Übersicht
                if user_id:
                    p_list_resp = session.get(f"{active_host}/PlantListAPI.do", params={"userId": user_id}, timeout=10)
                    if p_list_resp.status_code == 200:
                        p_j = p_list_resp.json()
                        plants_info = p_j.get("back") if isinstance(p_j.get("back"), dict) else p_j
                        if isinstance(plants_info.get("totalData"), dict):
                            raw_data["data"].update(plants_info["totalData"])
                        plant_arr = plants_info.get("data", [])
                        if plant_arr and isinstance(plant_arr, list):
                            first_plant = plant_arr[0]
                            if isinstance(first_plant, dict):
                                raw_data["data"].update(first_plant)
                                if isinstance(first_plant.get("plantData"), dict):
                                    raw_data["data"].update(first_plant["plantData"])
                            if not plant_id:
                                plant_id = str(first_plant.get("plantId") or first_plant.get("id") or "")
                                credentials["plant_id"] = plant_id

                # 2. Plant Detail API
                if plant_id:
                    try:
                        p_det_resp = session.get(
                            f"{active_host}/PlantDetailAPI.do",
                            params={"plantId": plant_id, "type": "1", "date": today_str},
                            timeout=10,
                        )
                        if p_det_resp.status_code == 200:
                            det_data = p_det_resp.json().get("back") or p_det_resp.json()
                            if isinstance(det_data, dict):
                                raw_data["data"].update(det_data)
                                if isinstance(det_data.get("plantData"), dict):
                                    raw_data["data"].update(det_data["plantData"])
                    except Exception as p_det_err:
                        logger.debug("PlantDetailAPI query failed: %s", p_det_err)

                # 3. Inverter Device Discovery für die Anlage
                discovered_devices = []
                if device_sn:
                    discovered_devices.append(device_sn)

                if plant_id:
                    for plant_ep, params, post_data in [
                        (
                            f"{active_host}/newTwoPlantAPI.do",
                            {"op": "getAllPlantListTwo"},
                            {
                                "language": "1",
                                "nominalPower": "",
                                "order": "1",
                                "pageSize": "15",
                                "plantName": "",
                                "plantStatus": "",
                                "toPageNum": "1",
                            },
                        ),
                        (f"{active_host}/newPlantAPI.do", {"op": "getPlantList"}, {"plantId": plant_id}),
                        (f"{active_host}/panel/getPlantData", None, {"plantId": plant_id}),
                        (f"{active_host}/panel/getPlantData", {"plantId": plant_id}, None),
                        (f"{active_host}/newPlantAPI.do", {"op": "getPlantData", "plantId": plant_id}, None),
                        (f"{active_host}/indexLogAPI.do", {"op": "getPlantData"}, {"plantId": plant_id}),
                    ]:
                        try:
                            if post_data is not None:
                                inv_list_resp = session.post(plant_ep, params=params, data=post_data, timeout=8)
                            else:
                                inv_list_resp = session.get(plant_ep, params=params, timeout=8)
                            if inv_list_resp.status_code == 200:
                                inv_data = inv_list_resp.json()
                                if isinstance(inv_data, dict):
                                    raw_data["data"].update(inv_data)
                                    for list_key in ["PlantList", "obj", "deviceList", "data", "invList", "storageList", "minList", "tlxList", "mixList", "spaList", "sphList"]:
                                        items = inv_data.get(list_key)
                                        if isinstance(items, list):
                                            for d in items:
                                                if isinstance(d, dict):
                                                    raw_data["data"].update(d)
                                                    sn = str(d.get("sn") or d.get("deviceSn") or d.get("inverterId") or d.get("datalogSn") or "").strip()
                                                    if sn and sn not in discovered_devices:
                                                        discovered_devices.append(sn)
                        except Exception:
                            pass

                if discovered_devices and not device_sn:
                    credentials["device_sn"] = discovered_devices[0]

                target_sn_list = discovered_devices if discovered_devices else ([device_sn] if device_sn else [])
                for sn in target_sn_list:
                    for inv_ep, params, data_payload in [
                        (f"{active_host}/newInverterAPI.do", {"op": "getInverterDetailData", "inverterId": sn}, None),
                        (f"{active_host}/newInverterAPI.do", {"op": "getInverterDetailData_two", "inverterId": sn}, None),
                        (f"{active_host}/newInverterAPI.do", {"op": "getInverterData", "id": sn, "type": "1", "date": today_str}, None),
                        (f"{active_host}/newTlxApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newTlxApi.do", {"op": "getSystemStatus_KW"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newMinApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newMinApi.do", {"op": "getSystemStatus_KW"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newMixApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newMixApi.do", {"op": "getSystemStatus_KW"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newSphApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newSphApi.do", {"op": "getSystemStatus_KW"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newMaxApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newSpaApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": sn}),
                        (f"{active_host}/newNoahApi.do", {"op": "getNoahDetailData"}, {"noahSn": sn}),
                    ]:
                        try:
                            if data_payload:
                                r = session.post(inv_ep, params=params, data=data_payload, timeout=8)
                            else:
                                r = session.get(inv_ep, params=params, timeout=8)
                            if r.status_code == 200:
                                j = r.json()
                                if isinstance(j, dict):
                                    d = j.get("obj") or j.get("back") or j.get("data") or j
                                    if isinstance(d, dict) and d:
                                        raw_data["data"].update(d)
                        except Exception:
                            pass
                    if inv_resp.status_code == 200:
                        inv_json = inv_resp.json()
                        if isinstance(inv_json, dict):
                            raw_data["data"].update(inv_json)

                    # Inverter Detail APIs für alle erkannten Wechselrichter
                    inverter_ids = []
                    if device_sn:
                        inverter_ids.append(device_sn)
                    obj_list = raw_data["data"].get("obj") or raw_data["data"].get("deviceList") or []
                    if isinstance(obj_list, list):
                        for dev in obj_list:
                            if isinstance(dev, dict):
                                sn = dev.get("sn") or dev.get("deviceSn") or dev.get("inverterId") or dev.get("datalogSn")
                                if sn and str(sn) not in inverter_ids:
                                    inverter_ids.append(str(sn))

                    today_str = timezone.now().strftime("%Y-%m-%d")
                    for inv_id in inverter_ids:
                        for inv_ep, params, data_payload in [
                            (f"{active_host}/newInverterAPI.do", {"op": "getInverterDetailData", "inverterId": inv_id}, None),
                            (f"{active_host}/newInverterAPI.do", {"op": "getInverterDetailData_two", "inverterId": inv_id}, None),
                            (f"{active_host}/newInverterAPI.do", {"op": "getInverterData", "id": inv_id, "type": "1", "date": today_str}, None),
                            (f"{active_host}/newTlxApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": inv_id}),
                            (f"{active_host}/newTlxApi.do", {"op": "getSystemStatus_KW"}, {"plantId": plant_id, "id": inv_id}),
                            (f"{active_host}/newMinApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": inv_id}),
                            (f"{active_host}/newMixApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": inv_id}),
                            (f"{active_host}/newSphApi.do", {"op": "getEnergyOverview"}, {"plantId": plant_id, "id": inv_id}),
                        ]:
                            try:
                                if data_payload:
                                    r = session.post(inv_ep, params=params, data=data_payload, timeout=8)
                                else:
                                    r = session.get(inv_ep, params=params, timeout=8)
                                if r.status_code == 200:
                                    j = r.json()
                                    if isinstance(j, dict):
                                        d = j.get("obj") or j.get("back") or j.get("data") or j
                                        if isinstance(d, dict) and d:
                                            raw_data["data"].update(d)
                            except Exception:
                                pass

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
    Testet eingegebene Zugangsdaten über die modulare Adapter-Registry.
    Vollständig entkoppelt und hersteller-isoliert.
    """
    from devices.adapters.registry import get_adapter
    adapter = get_adapter(profile_id)
    res = adapter.test_connection(credentials)
    return {
        "status": res.status,
        "message": res.message,
        "live_metrics": res.live_metrics,
        "raw_sample": res.raw_sample,
        "simulated": res.simulated,
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
                    is_empty_or_zero = v in (None, "", "-", "--", "null", "none", "0", "0.0", "0.00", "0 W", "0W", "0 kW", "0kW", 0, 0.0, False)
                    if k not in flat or (flat[k] in (None, "", "-", "--", "null", "none", "0", "0.0", "0.00", "0 W", "0W", "0 kW", "0kW", 0, 0.0, False) and not is_empty_or_zero):
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
    intelligente Multi-Key Fallbacks mit automatischer Einheitenbereinigung (z. B. für Sungrow, Growatt etc.).
    """
    mapping = profile.get("metrics_mapping", {})
    extracted = {}

    # Vollständiger Fallback-Pool inklusive aller verschachtelten Listen & Dictionaries
    data_dict = _flatten_payload_dict(raw_payload)

    for metric_name, rule in mapping.items():
        jsonpath = rule.get("jsonpath")
        rule_scale = float(rule.get("scale", 1.0))
        fallback = rule.get("fallback")
        transform = rule.get("transform")
        min_val = rule.get("min")
        max_val = rule.get("max")
        target_unit = "kWh" if "kwh" in metric_name else ("%" if "soc" in metric_name else "W")

        raw_val = extract_jsonpath(raw_payload, jsonpath, fallback=None)
        unit_already_converted = False

        if raw_val is not None:
            if isinstance(raw_val, str):
                s_low = raw_val.lower()
                if any(u in s_low for u in ["kw", "mw", "kwh", "mwh", "wh", "%"]):
                    unit_already_converted = True
            raw_val = _clean_numeric_value(raw_val, target_unit=target_unit)

        # Intelligente Multi-Key Fallbacks falls JSONPath keinen Treffer liefert
        if raw_val is None:
            if metric_name == "pv_power_w":
                for k in [
                    "curr_power", "curr_pac", "currPower", "currPac", "currentPower", "current_power",
                    "currentEnergy", "current_energy", "pac", "ppv", "ppv1", "ppv2", "pPv1", "pPv2",
                    "nominalPower", "invPac", "power", "pv_power",
                    "pvPower", "pAct", "pact", "pac1", "ppvTotal", "p_pv", "p_pv1", "p_pv2", "total_power"
                ]:
                    if k in data_dict and data_dict[k] is not None:
                        if isinstance(data_dict[k], str) and any(u in data_dict[k].lower() for u in ["kw", "mw", "w"]):
                            unit_already_converted = True
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="W")
                        if clean_v is not None:
                            if not unit_already_converted and k in ("currentPower", "current_power", "currPower", "curr_power", "nominalPower", "total_power", "invPac", "plantPower") and 0.0 < abs(clean_v) <= 100.0:
                                clean_v = clean_v * 1000.0
                                unit_already_converted = True
                            raw_val = clean_v
                            if k not in ("curr_power", "currPower", "power", "currentPower"):
                                unit_already_converted = True
                            break

            elif metric_name == "battery_soc":
                for k in [
                    "curr_soc", "curr_battery_soc", "soc", "batterySoc", "battery_soc",
                    "batteryPercent", "chargeLevel", "capacity", "SOC", "storageSoc", "battery_level"
                ]:
                    if k in data_dict and data_dict[k] is not None:
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="%")
                        if clean_v is not None:
                            raw_val = clean_v
                            break

            elif metric_name == "battery_power_w":
                for k in [
                    "curr_battery_power", "battery_power", "batteryPower", "p_battery",
                    "pdisCharge", "pcharge", "pdisCharge1", "pcharge1", "pactostorage", "pstorage",
                    "pDisCharge", "pCharge", "battery_power_w", "batteryPowerW", "B_P1"
                ]:
                    if k in data_dict and data_dict[k] is not None:
                        if isinstance(data_dict[k], str) and any(u in data_dict[k].lower() for u in ["kw", "mw", "w"]):
                            unit_already_converted = True
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="W")
                        if clean_v is not None:
                            raw_val = clean_v
                            if k not in ("curr_battery_power", "battery_power"):
                                unit_already_converted = True
                            break

            elif metric_name == "grid_power_w":
                for k in [
                    "curr_grid_power", "grid_power", "gridPower", "p_grid", "pgrid", "pactogrid",
                    "toGridPower", "to_grid_power", "pGrid", "feed_in_power", "p_feed_in",
                    "gridPurchasedPower", "grid_power_w", "gridPowerW"
                ]:
                    if k in data_dict and data_dict[k] is not None:
                        if isinstance(data_dict[k], str) and any(u in data_dict[k].lower() for u in ["kw", "mw", "w"]):
                            unit_already_converted = True
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="W")
                        if clean_v is not None:
                            raw_val = clean_v
                            if k not in ("curr_grid_power", "grid_power"):
                                unit_already_converted = True
                            break

            elif metric_name == "load_power_w":
                for k in [
                    "pactouser", "pacToUserTotal", "pLocalLoad", "pToUser",
                    "curr_load_power", "load_power", "loadPower", "p_load", "pload", "use_power",
                    "use_power_w", "useEnergy", "familyLoadPower", "consumption",
                    "loadPowerW", "home_load"
                ]:
                    if k in data_dict and data_dict[k] is not None:
                        if isinstance(data_dict[k], str) and any(u in data_dict[k].lower() for u in ["kw", "mw", "w"]):
                            unit_already_converted = True
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="W")
                        if clean_v is not None:
                            raw_val = clean_v
                            if k not in ("curr_load_power", "load_power"):
                                unit_already_converted = True
                            break

            elif metric_name == "daily_generation_kwh":
                for k in [
                    "today_energy", "todayEnergy", "today_yield", "todayYield", "eToday",
                    "etoday", "e_today", "eTodayTotal", "eAcChargeToday", "daily_generation",
                    "solar_yield", "daily_yield"
                ]:
                    if k in data_dict and data_dict[k] is not None:
                        clean_v = _clean_numeric_value(data_dict[k], target_unit="kWh")
                        if clean_v is not None:
                            raw_val = clean_v
                            break

        if raw_val is None:
            raw_val = fallback

        if raw_val is not None:
            try:
                val = float(raw_val)

                # Intelligente Skalierung:
                # 1. Wenn Einheit bereits explizit konvertiert oder Key in Watt vorlag -> kein Multiplizieren mit 1000
                # 2. Wenn scale == 1000.0, aber Betrag >= 300.0 (kW > 300 bei EFH unmöglich) -> bereits Watt
                if unit_already_converted:
                    effective_scale = 1.0
                elif rule_scale == 1000.0 and abs(val) >= 300.0:
                    effective_scale = 1.0
                elif rule_scale == 0.001 and abs(val) <= 100.0:
                    effective_scale = 1.0
                else:
                    effective_scale = rule_scale

                val = val * effective_scale

                if transform == "abs":
                    val = abs(val)
                elif transform == "invert":
                    val = -val

                # SoC Normalisierung: falls als Dezimal 0.0 - 1.0 vorliegt
                if metric_name == "battery_soc":
                    if 0.0 <= val <= 1.0:
                        val = val * 100.0

                if min_val is not None and val < float(min_val):
                    val = float(min_val)
                if max_val is not None and val > float(max_val):
                    val = float(max_val)

                extracted[metric_name] = round(val, 2)
            except (ValueError, TypeError):
                extracted[metric_name] = fallback
        else:
            extracted[metric_name] = fallback

    # Physikalische Plausibilisierung für Grid & Load Vorzeichen
    pv_val = float(extracted.get("pv_power_w") or 0.0)
    bat_val = float(extracted.get("battery_power_w") or 0.0)
    load_val = float(extracted.get("load_power_w") or 0.0) if extracted.get("load_power_w") is not None else None
    grid_val = float(extracted.get("grid_power_w")) if extracted.get("grid_power_w") is not None else None

    if grid_val is not None:
        bat_charging = abs(min(0.0, bat_val))
        bat_discharging = max(0.0, bat_val)
        eff_load = load_val if (load_val is not None and load_val > 0) else 0.0

        if pv_val > 50.0:
            surplus = pv_val + bat_discharging - eff_load - bat_charging
            if surplus > 30.0:
                if grid_val > 0:
                    extracted["grid_power_w"] = -abs(grid_val)
                elif grid_val == 0.0 and surplus > 50.0 and load_val is not None:
                    extracted["grid_power_w"] = -round(surplus, 1)
            elif eff_load > (pv_val + bat_discharging + 30.0):
                if grid_val < 0:
                    extracted["grid_power_w"] = abs(grid_val)

        if (load_val is None or load_val <= 0.0) and pv_val > 50.0:
            cur_grid = float(extracted.get("grid_power_w", 0.0) or 0.0)
            if cur_grid > 0 and abs(cur_grid - pv_val) < (pv_val * 0.5 + 500):
                cur_grid = -abs(cur_grid)
                extracted["grid_power_w"] = cur_grid
            extracted["load_power_w"] = max(0.0, round(pv_val + cur_grid + bat_val, 1))

    return extracted


def execute_cloud_poll(integration: CloudDeviceIntegration) -> dict:
    """
    Führt einen regulären Polling-Zyklus für ein CloudDeviceIntegration-Objekt durch.
    Nutzt den modularen Adapter und die Standard Canonical Ingest Pipeline.
    """
    profile_id = integration.profile_id
    credentials = integration.credentials or {}
    device = integration.device

    try:
        from devices.adapters.registry import get_adapter
        from devices.adapters.ingest_core import process_canonical_telemetry

        adapter = get_adapter(profile_id)
        telemetry = adapter.fetch_telemetry(credentials)
        metrics = process_canonical_telemetry(
            device=device,
            telemetry=telemetry,
            source="cloud_poll",
            device_name=credentials.get("ps_name"),
            battery_capacity_kwh=credentials.get("battery_capacity_kwh"),
        )
        now = timezone.now()

        # Status und ggf. aktualisierte Tokens (OAuth refresh) persistieren
        integration.credentials = credentials
        integration.last_polled_at = now
        integration.last_status = CloudDeviceIntegration.STATUS_OK
        integration.last_error_message = ""
        integration.save(update_fields=["credentials", "last_polled_at", "last_status", "last_error_message", "updated_at"])

        logger.info("Successfully polled cloud integration %s for device %s: %s", profile_id, device.id, metrics)
        return {
            "status": "success",
            "metrics": metrics,
            "device_id": str(device.id),
            "polled_at": now.isoformat(),
        }
    except Exception as e:
        logger.exception("Error polling cloud integration %s for device %s: %s", profile_id, device.id, e)
        integration.credentials = credentials
        integration.last_polled_at = timezone.now()
        integration.last_status = CloudDeviceIntegration.STATUS_ERROR
        integration.last_error_message = str(e)
        integration.save(update_fields=["credentials", "last_polled_at", "last_status", "last_error_message", "updated_at"])
        return {
            "status": "error",
            "error": str(e),
            "device_id": str(device.id),
        }

