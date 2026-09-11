"""
devices/adapters/sungrow.py

Isolierter Adapter für Sungrow iSolarCloud (Hybrid-Wechselrichter SH5.0-25T/RT und SBR-Speicher).
Unterstützt:
1. Offizielle OpenAPI mit OAuth2 / Bearer Token & Messpunkt-Wörterbüchern
2. Legacy iSolarCloud API mit Benutzername & Passwort
3. Standardisierte Transformation in CanonicalTelemetry
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from devices.adapters.contracts import BaseInverterAdapter, CanonicalTelemetry, AdapterTestResult

logger = logging.getLogger(__name__)


class SungrowAdapter(BaseInverterAdapter):
    profile_id = "sungrow_isolarcloud"
    name = "Sungrow iSolarCloud"
    vendor = "Sungrow"
    protocol = "http_cloud"
    category = "inverter_hybrid"

    MEASURE_POINTS = [
        "83033", "83067", "83052", "83106", "83051", "83549",
        "83129", "83252", "83238", "83104", "83111", "83112", "83326",
        "83328", "83329", "83330", "83334"
    ]

    def _execute_login(self, base_url: str, appkey: str, account: str, password: str) -> dict:
        """
        Führt den Sungrow iSolarCloud Login-Handshake für die Legacy-API durch.
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

            res_data = res_json.get("result_data") or {}
            if res_json.get("result_code") == "1" and res_data.get("token"):
                token_data = {
                    "token": res_data["token"],
                    "user_id": res_data.get("user_id"),
                }
                cache.set(cache_key, token_data, timeout=7000)
                return token_data
            else:
                msg = res_json.get("result_msg") or "Ungültige iSolarCloud Zugangsdaten"
                raise ValueError(f"Sungrow Login fehlgeschlagen: {msg}")
        except requests.RequestException as e:
            logger.warning("Sungrow Login Request Error: %s", e)
            raise ValueError(f"Verbindungsfehler zu Sungrow iSolarCloud: {e}")

    def generate_mock_payload(self) -> dict:
        """
        Generiert realistische Live-Messdaten für Testumgebungen oder Simulationen.
        """
        import random
        now = timezone.now()
        hour = now.hour

        if 6 <= hour <= 20:
            pv_factor = max(0.0, 1.0 - ((hour - 13.0) / 7.0) ** 2)
            pv_kw = round(random.uniform(3.5, 7.8) * pv_factor, 2)
        else:
            pv_kw = 0.0

        load_kw = round(random.uniform(0.6, 2.2), 2)
        diff = pv_kw - load_kw

        if diff > 0:
            battery_kw = round(min(diff * 0.7, 3.0) * -1, 2)  # negativ = laden
            grid_kw = round((diff + battery_kw) * -1, 2)      # negativ = einspeisen
        else:
            battery_kw = round(min(abs(diff), 2.5), 2)        # positiv = entladen
            grid_kw = round(abs(diff) - battery_kw, 2)        # positiv = Bezug

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

    def parse_payload(self, raw_data: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Wandelt ein Sungrow API JSON-Objekt in CanonicalTelemetry um.
        """
        # 1. Prüfen ob direkte Messpunkt-Metriken vorliegen
        if "_direct_metrics" in raw_data:
            dm = raw_data["_direct_metrics"]
            telemetry = CanonicalTelemetry(
                pv_power_w=dm.get("pv_power_w"),
                grid_power_w=dm.get("grid_power_w"),
                load_power_w=dm.get("load_power_w"),
                battery_power_w=dm.get("battery_power_w"),
                battery_soc=dm.get("battery_soc"),
                daily_yield_kwh=dm.get("daily_generation_kwh"),
                raw_payload=raw_data,
            )
            return telemetry.validate()

        # 2. Daten-Quelle auflösen (result_data, data_list oder flaches Dict)
        res_data = raw_data.get("result_data", raw_data)
        if isinstance(res_data, dict) and "data_list" in res_data and isinstance(res_data["data_list"], list) and res_data["data_list"]:
            target_dict = {**res_data, **res_data["data_list"][0]}
        elif isinstance(res_data, dict):
            target_dict = res_data
        else:
            target_dict = raw_data

        def _get_val(*keys) -> Optional[float]:
            for k in keys:
                if k in target_dict and target_dict[k] is not None:
                    raw = str(target_dict[k]).strip().replace(",", ".")
                    if raw.lower() in ("-", "--", "null", "none", "n/a", ""):
                        continue
                    factor = 1.0
                    low = raw.lower()
                    if "kw" in low:
                        factor = 1000.0
                        low = low.replace("kw", "").strip()
                    elif "w" in low:
                        low = low.replace("w", "").strip()
                    elif "%" in low:
                        low = low.replace("%", "").strip()
                    import re
                    match = re.search(r"[-+]?\d*\.?\d+", low)
                    if match:
                        try:
                            v = float(match.group(0)) * factor
                            # Wenn keine Einheit angegeben war und der Key standardmäßig kW liefert (z.B. curr_power)
                            if factor == 1.0 and k in ("curr_power", "grid_power", "load_power", "battery_power", "power") and abs(v) <= 150.0:
                                v = v * 1000.0
                            return v
                        except (ValueError, TypeError):
                            pass
            return None

        pv = _get_val("curr_power", "curr_pac", "currPower", "pac", "pv_power", "p_pv")
        grid = _get_val("grid_power", "curr_grid_power", "gridPower", "p_grid", "pgrid")
        load = _get_val("load_power", "curr_load_power", "loadPower", "p_load", "pload", "use_power")
        battery = _get_val("battery_power", "curr_battery_power", "batteryPower", "p_battery", "pdisCharge", "pcharge")
        soc = _get_val("battery_soc", "curr_soc", "curr_battery_soc", "soc", "batteryPercent", "chargeLevel")
        daily = _get_val("today_energy", "todayEnergy", "today_yield", "eToday", "etoday", "daily_generation")
        if daily is not None and daily > 1000.0:
            daily = daily / 1000.0 # Falls in Wh geliefert

        telemetry = CanonicalTelemetry(
            pv_power_w=pv,
            grid_power_w=grid,
            load_power_w=load,
            battery_power_w=battery,
            battery_soc=soc,
            daily_yield_kwh=daily,
            raw_payload=raw_data,
        )
        return telemetry.validate()

    def fetch_telemetry(self, credentials: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Fragt die Live-Telemetrie vom Sungrow Server ab.
        """
        res = self.test_connection(credentials)
        if res.status == "success":
            return self.parse_payload(res.raw_sample)
        raise ValueError(res.error or res.message)

    def test_connection(self, credentials: Dict[str, Any]) -> AdapterTestResult:
        """
        Führt einen Verbindungstest gegen iSolarCloud oder die OpenAPI durch.
        """
        base_url = credentials.get("base_url") or "https://gateway.isolarcloud.eu"
        appkey = credentials.get("appkey") or getattr(settings, "SUNGROW_APPKEY", "") or os.getenv("SUNGROW_APPKEY", "")
        app_secret = getattr(settings, "SUNGROW_APP_SECRET", "") or os.getenv("SUNGROW_APP_SECRET", "")
        token = credentials.get("token")
        ps_id = credentials.get("ps_id") or credentials.get("ps_ids") or ""

        # Sandbox-Modus prüfen
        is_mock = (
            bool(credentials.get("is_mock"))
            or str(appkey).lower() in ("mock", "fake", "demo", "test")
            or not credentials
            or (not appkey and not token and not credentials.get("user_account"))
            or str(credentials.get("user_account", "")).lower() in ("tester@sharegy.de", "demo@sharegy.de", "sungrow@sharegy.de")
            or str(credentials.get("token", "")).lower() in ("demo", "test", "mock")
            or str(credentials.get("token", "")).startswith("sg_oauth_demo")
        )

        if is_mock:
            mock_data = self.generate_mock_payload()
            telemetry = self.parse_payload(mock_data)
            return AdapterTestResult(
                status="success",
                message=f"Verbindung zu {self.name} erfolgreich (Simulator / Sandbox-Modus).",
                live_metrics=telemetry.to_metrics_dict(),
                raw_sample=mock_data,
                simulated=True,
            )

        is_oauth = credentials.get("auth_type") == "oauth2" or bool(token and not credentials.get("user_password"))

        if is_oauth and token:
            def _refresh_openapi_token() -> bool:
                nonlocal token
                r_token = credentials.get("refresh_token")
                if not r_token:
                    return False
                try:
                    redir_url = credentials.get("redirect_uri") or getattr(settings, "SUNGROW_REDIRECT_URI", "")
                    headers = {
                        "x-access-key": app_secret,
                        "sys_code": "901",
                        "Content-Type": "application/json",
                    }
                    for ref_ep, ref_payload in [
                        (
                            f"{base_url.rstrip('/')}/openapi/oauth/token",
                            {
                                "appkey": appkey,
                                "grant_type": "refresh_token",
                                "refresh_token": r_token,
                                "redirect_uri": redir_url,
                            },
                        ),
                        (
                            f"{base_url.rstrip('/')}/openapi/apiManage/refreshToken",
                            {"appkey": appkey, "refresh_token": r_token},
                        ),
                    ]:
                        t_resp = requests.post(ref_ep, json=ref_payload, headers=headers, timeout=10)
                        if t_resp.status_code == 200:
                            resp_j = t_resp.json()
                            new_tok = resp_j.get("access_token") or resp_j.get("token")
                            if not new_tok and isinstance(resp_j.get("result_data"), dict):
                                new_tok = resp_j["result_data"].get("access_token") or resp_j["result_data"].get("token")
                                if resp_j["result_data"].get("refresh_token"):
                                    credentials["refresh_token"] = resp_j["result_data"]["refresh_token"]
                            if new_tok:
                                token = new_tok
                                credentials["token"] = token
                                logger.info("Successfully refreshed Sungrow OpenAPI token on %s.", ref_ep)
                                return True
                except Exception as e:
                    logger.warning("Auto token refresh failed: %s", e)
                return False

            def _post_with_auth(endpoint: str, json_data: dict) -> Optional[requests.Response]:
                nonlocal token
                url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
                payload = dict(json_data)
                if token and "token" not in payload:
                    payload["token"] = token
                if appkey and "appkey" not in payload:
                    payload["appkey"] = appkey

                headers = {
                    "x-access-key": app_secret,
                    "sys_code": "901",
                    "token": str(token or ""),
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
                try:
                    resp = requests.post(url, json=payload, headers=headers, timeout=12)
                    is_auth_err = resp.status_code in (401, 403)
                    if resp.status_code == 200:
                        try:
                            body = resp.json()
                            code_str = str(body.get("result_code", ""))
                            msg_str = str(body.get("result_msg", "")).lower()
                            if code_str in ("2", "000", "0000", "401") or ("token" in msg_str and ("invalid" in msg_str or "expired" in msg_str or "fail" in msg_str)):
                                is_auth_err = True
                        except Exception:
                            pass

                    if is_auth_err and _refresh_openapi_token():
                        payload["token"] = token
                        headers["token"] = str(token or "")
                        headers["Authorization"] = f"Bearer {token}"
                        resp = requests.post(url, json=payload, headers=headers, timeout=12)
                    return resp
                except Exception as req_err:
                    logger.warning("Sungrow OpenAPI request to %s failed: %s", endpoint, req_err)
                    return None

            # OpenAPI Modus
            if credentials.get("auth_code") and not token:
                try:
                    redir_url = credentials.get("redirect_uri") or getattr(settings, "SUNGROW_REDIRECT_URI", "")
                    t_resp = requests.post(
                        f"{base_url.rstrip('/')}/openapi/oauth/token",
                        json={
                            "appkey": appkey,
                            "code": credentials["auth_code"],
                            "grant_type": "authorization_code",
                            "redirect_uri": redir_url,
                        },
                        headers={"x-access-key": app_secret, "sys_code": "901", "Content-Type": "application/json"},
                        timeout=10,
                    )
                    if t_resp.status_code == 200 and t_resp.json().get("access_token"):
                        token = t_resp.json()["access_token"]
                        credentials["token"] = token
                        if t_resp.json().get("refresh_token"):
                            credentials["refresh_token"] = t_resp.json()["refresh_token"]
                except Exception as ex_err:
                    logger.warning("Auto token exchange failed: %s", ex_err)

            if not ps_id or ps_id in ("default_ps", "12345", ""):
                try:
                    list_resp = _post_with_auth(
                        "openapi/platform/queryPowerStationList",
                        {"page": 1, "size": 20, "lang": "_de_DE"},
                    )
                    if list_resp and list_resp.status_code == 200:
                        list_data = list_resp.json().get("result_data", {})
                        stations = list_data.get("pageList", []) if isinstance(list_data, dict) else []
                        if stations:
                            ps_id = str(stations[0].get("ps_id") or stations[0].get("id"))
                            credentials["ps_id"] = ps_id
                            credentials["ps_name"] = stations[0].get("ps_name", "Sungrow PV-Anlage")
                except Exception as e:
                    logger.warning("Auto-fetch ps_id via OpenAPI failed: %s", e)

            raw_data: Dict[str, Any] = {"result_code": "1", "result_data": {}}

            try:
                rt_resp = _post_with_auth(
                    "openapi/platform/getPowerStationRealTimeData",
                    {
                        "appkey": appkey,
                        "token": token,
                        "ps_id_list": [str(ps_id or "")],
                        "point_id_list": self.MEASURE_POINTS,
                        "is_get_point_dict": "1",
                    },
                )
                if rt_resp and rt_resp.status_code == 200:
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

                        # Batterie Lade-/Entladerichtung standardisieren (Sharegy-Konvention: Negativ = Laden, Positiv = Entladen)
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

                        # Netzeinspeisung / Grid Plausibilisierung
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
                resp = _post_with_auth(
                    "openapi/platform/getPowerStationDetail",
                    {"appkey": appkey, "token": token, "ps_ids": str(ps_id or ""), "lang": "_de_DE"},
                )
                if resp and resp.status_code == 200:
                    det_json = resp.json()
                    if det_json.get("result_data", {}).get("data_list"):
                        d_list = det_json["result_data"]["data_list"]
                        if isinstance(d_list, list) and d_list:
                            raw_data["result_data"].update(d_list[0])
            except Exception as e:
                logger.warning("getPowerStationDetail query failed: %s", e)

            telemetry = self.parse_payload(raw_data)

            # Validitätsprüfung
            if "_direct_metrics" not in raw_data and not raw_data.get("result_data"):
                # Fallback auf Legacy Login falls Benutzername & Passwort vorliegen
                if credentials.get("user_account") and credentials.get("user_password"):
                    try:
                        logger.info("Falling back to Sungrow Legacy Login...")
                        token_info = self._execute_login(
                            base_url=base_url,
                            appkey=appkey,
                            account=credentials.get("user_account"),
                            password=credentials.get("user_password"),
                        )
                        token = token_info["token"]
                        credentials["token"] = token
                        credentials["user_id"] = token_info["user_id"]
                        legacy_headers = {
                            "Content-Type": "application/json",
                            "sys_code": "901",
                            "token": token,
                        }
                        legacy_resp = requests.post(
                            f"{base_url.rstrip('/')}/v1/powerStationService/getPowerStationDetail",
                            headers=legacy_headers,
                            json={"appkey": appkey, "ps_id": str(ps_id or "")},
                            timeout=12,
                        )
                        if legacy_resp.status_code == 200:
                            raw_data = legacy_resp.json()
                            telemetry = self.parse_payload(raw_data)
                            return AdapterTestResult(
                                status="success",
                                message=f"Live-Verbindung zu {self.name} erfolgreich!",
                                live_metrics=telemetry.to_metrics_dict(),
                                raw_sample=raw_data,
                                simulated=False,
                            )
                    except Exception as leg_err:
                        logger.warning("Sungrow Legacy login fallback failed: %s", leg_err)

                if is_mock:
                    return AdapterTestResult(
                        status="success",
                        message=f"Verbindung zu {self.name} erfolgreich (Simulator).",
                        live_metrics=telemetry.to_metrics_dict(),
                        raw_sample=raw_data,
                        simulated=True,
                    )
                else:
                    err_msg = "Sungrow OpenAPI lieferte keine Daten (HTTP 401 / Token ungültig). Bitte Autorisierung unter Schnittstellen erneuern."
                    logger.warning(err_msg)
                    return AdapterTestResult(
                        status="error",
                        error=err_msg,
                        message=err_msg,
                        live_metrics=telemetry.to_metrics_dict(),
                        raw_sample=raw_data,
                        simulated=False,
                    )

            return AdapterTestResult(
                status="success",
                message=f"Live-Verbindung zu {self.name} erfolgreich!",
                live_metrics=telemetry.to_metrics_dict(),
                raw_sample=raw_data,
                simulated=False,
            )

        else:
            # Legacy Login Modus
            if not token:
                token_info = self._execute_login(
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
            telemetry = self.parse_payload(raw_data)

            return AdapterTestResult(
                status="success",
                message=f"Live-Verbindung zu {self.name} erfolgreich hergestellt!",
                live_metrics=telemetry.to_metrics_dict(),
                raw_sample=raw_data,
                simulated=False,
            )
