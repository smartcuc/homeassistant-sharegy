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

            # 1. Realtime Measurement Points abfragen (Offizielle Sungrow OpenAPI)
            # Nur echte, sekündliche Momentan-Leistungswerte (W) und SoC (%) abfragen.
            # Kumulierte Tageszähler von Sungrow werden NICHT verwendet, da diese erst zeitverzögert
            # oder am Folgetag von Sungrows Cloud aggregiert werden. Sharegy aggregiert die realen Messwerte selbst!
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
                        # Robustes Dict aufbauen: Keys mit und ohne 'p' Präfix
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

                        # Netz-Kandidaten (83051 ist der offizielle Netzübergabepunkt DTSU666)
                        grid = _get_pt("83051", "83549", "83328") or 0.0

                        # Batterie-Leistung Kandidaten
                        bat_pwr = _get_pt("83104", "83238", "83111", "83112", "83326") or 0.0

                        # SoC Prozentwert ermitteln (0.348 -> 34.8 %)
                        soc_raw = _get_pt("83129", "83252", "83334")
                        soc_val = None
                        if soc_raw is not None:
                            if 0.0 <= soc_raw <= 1.0:
                                soc_val = round(soc_raw * 100.0, 1)
                            else:
                                soc_val = round(soc_raw, 1)

                        # Batterie Lade-/Entladerichtung standardisieren (Sharegy-Konvention: Negativ = Laden, Positiv = Entladen):
                        # 1. Wenn Speicher voll ist (>= 98%), kann physikalisch kein Strom mehr geladen werden
                        if soc_val is not None and soc_val >= 98.0:
                            if bat_pwr < 0:
                                bat_pwr = 0.0
                        # 2. PV-Überschuss vorhanden (PV > Load + 30 W) und Speicher nicht voll (SoC < 98%):
                        # Wenn bat_pwr positiv gemeldet wurde oder der Inverter absolute Ladeleistung sendet,
                        # ist dies physikalisch LADUNG (negatives Vorzeichen)
                        elif pv > (load + 30) and (soc_val is None or soc_val < 98.0) and abs(bat_pwr) > 10:
                            bat_pwr = -abs(bat_pwr)
                        # 3. Nacht / keine PV (PV < 20 W) und Speicher hat Kapazität (> 5%):
                        # Speicher entlädt zur Deckung der Last (positives Vorzeichen)
                        elif pv < 20 and soc_val is not None and soc_val > 5.0 and load > 20:
                            if abs(bat_pwr) < 0.1 and abs(grid) < 60:
                                bat_pwr = load
                            else:
                                bat_pwr = abs(bat_pwr)

                        # 4. Netzeinspeisung / Grid Plausibilisierung:
                        # Wenn der Speicher lädt (bat_pwr < 0), fließt PV-Leistung in den Speicher.
                        # Falls das SmartMeter/API versehentlich die Batterieladung als Netzeinspeisung meldet:
                        if bat_pwr < 0:
                            bat_charge = abs(bat_pwr)
                            # Tatsächliche Netzeinspeisung ist maximal der Überschuss NACH Batterieladung und Hauslast
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
                    # Falls Token abgelaufen ist, Refresh versuchen
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
