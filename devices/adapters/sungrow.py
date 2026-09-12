"""
devices/adapters/sungrow.py

Offizieller, isolierter OpenAPI-Adapter für Sungrow iSolarCloud (Hybrid-Wechselrichter SH-Serie und SBR-Speicher).
Ausschließliche Nutzung der offiziellen iSolarCloud OpenAPI mit OAuth 2.0 / Bearer Token & Messpunkt-Wörterbüchern.
Standardisierte Transformation in CanonicalTelemetry mit physikalisch exakter Einspeisungs- und Lastbilanz.
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone

from devices.adapters.contracts import BaseInverterAdapter, CanonicalTelemetry, AdapterTestResult

logger = logging.getLogger(__name__)


class SungrowAdapter(BaseInverterAdapter):
    profile_id = "sungrow_isolarcloud"
    name = "Sungrow iSolarCloud"
    vendor = "Sungrow"
    protocol = "http_cloud"
    category = "inverter_hybrid"

    MEASURE_POINTS = [
        "83022", "83024", "83033", "83019", "83006", "83020", "83011", "83021",
        "83032", "83007", "83002", "83009", "83004", "83012", "83013", "83023",
        "83005", "83025", "83018", "83001", "83008", "83010", "83016", "83017",
        "83046", "83052", "83067", "83097", "83100", "83102", "83105", "83106",
        "83118", "83124", "83119", "83072", "83075", "83252", "83129", "83232",
        "83233", "83234", "83235", "83236", "83237", "83238", "83239", "83240",
        "83243", "83241", "83244", "83242", "83548", "83549", "83419", "83317",
        "83318", "83319", "83320", "83321", "83322", "83324", "83323", "83325",
        "83327", "83326", "83328", "83329", "83330", "83331", "83332", "83334", "83335"
    ]

    def generate_mock_payload(self) -> dict:
        """
        Generiert realistische Live-Messdaten für Testumgebungen oder Simulationen.
        """
        import random
        # Realistische PV-Leistung für Simulation/Sandbox
        pv_kw = round(random.uniform(3.5, 7.8), 2)

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

        def _get_val_pos(*keys) -> Optional[float]:
            for k in keys:
                v = _get_val(k)
                if v is not None and v > 0.0:
                    return v
            return None

        pv_direct = _get_val_pos("curr_power", "curr_pac", "currPower", "pac", "pv_power", "p_pv", "total_power", "p_dc")
        ppv1 = _get_val_pos("ppv1", "pPv1", "p_pv1", "mppt1_power", "p1") or 0.0
        ppv2 = _get_val_pos("ppv2", "pPv2", "p_pv2", "mppt2_power", "p2") or 0.0
        ppv_sum = ppv1 + ppv2

        pv_candidates = [v for v in [pv_direct, ppv_sum if ppv_sum > 0 else None, _get_val("curr_power", "curr_pac", "currPower", "pac", "pv_power", "p_pv")] if v is not None]
        pv = max(pv_candidates) if pv_candidates else 0.0
        grid = _get_val("grid_power", "curr_grid_power", "gridPower", "p_grid", "pgrid")
        load = _get_val("load_power", "curr_load_power", "loadPower", "p_load", "pload", "use_power")
        battery = _get_val("battery_power", "curr_battery_power", "batteryPower", "p_battery", "pdisCharge", "pcharge")
        soc = _get_val("battery_soc", "curr_soc", "curr_battery_soc", "soc", "batteryPercent", "chargeLevel")
        daily = _get_val("today_energy", "todayEnergy", "today_yield", "eToday", "etoday", "daily_generation")
        if daily is not None and daily > 1000.0:
            daily = daily / 1000.0 # Falls in Wh geliefert

        pv_val = max(0.0, float(pv or 0.0))
        bat_val = float(battery or 0.0)
        soc_val = float(soc) if soc is not None else None

        # Batterie Leistung & Richtung plausibilisieren / ableiten falls nicht direkt gemeldet:
        if abs(bat_val) < 1.0 and soc_val is not None and load is not None:
            deficit = float(load) - pv_val - max(0.0, float(grid or 0.0))
            if deficit > 10.0 and soc_val > 5.0:
                bat_val = round(deficit, 1)  # Positiv = Entladen (Discharge ins Haus)
                battery = bat_val
            elif (pv_val - float(load) + min(0.0, float(grid or 0.0))) > 10.0 and soc_val < 98.0:
                surplus = pv_val - float(load) + min(0.0, float(grid or 0.0))
                bat_val = -round(surplus, 1)  # Negativ = Laden (Charge aus PV)
                battery = bat_val
        elif soc_val is not None:
            if soc_val >= 98.0 and bat_val < 0:
                bat_val = 0.0
                battery = 0.0
            elif soc_val <= 5.0 and bat_val > 0:
                bat_val = 0.0
                battery = 0.0

        bat_charging = abs(min(0.0, bat_val))
        bat_discharging = max(0.0, bat_val)

        if grid is not None:
            grid_val = float(grid)
            load_val = float(load) if (load is not None and float(load) > 0) else None

            # Fall A: Inverter meldet grid_power > 0, aber PV liefert signifikante Erzeugung
            if pv_val > 50.0 and abs(grid_val) > 10.0:
                # Wenn load_val fehlt oder verdächtig gleich pv_val ist (häufiger Inverter-FW-Effekt):
                if load_val is None or abs(load_val - pv_val) < 50.0 or (grid_val > 0 and grid_val >= (pv_val * 0.6)):
                    # Eindeutige Netzeinspeisung: grid muss negativ sein
                    grid = -abs(grid_val)
                    # Hausverbrauch ist physisch die verbleibende Restleistung:
                    load = max(0.0, round(pv_val + float(grid) - bat_charging + bat_discharging, 1))
                else:
                    # load_val ist plausibel unabhängig gemessen:
                    surplus = pv_val + bat_discharging - load_val - bat_charging
                    if surplus > 30.0:
                        grid = -abs(grid_val)
                    elif load_val > (pv_val + bat_discharging + 30.0):
                        grid = abs(grid_val)

            # Fall B: Keine PV (Nacht / < 20W) -> grid_power > 0 ist echter Netzbezug
            elif pv_val < 20.0 and grid_val < 0 and (load_val is None or load_val > 20.0) and bat_discharging < 20.0:
                grid = abs(grid_val)

            # Fall C: Load berechnen falls noch leer
            if (load is None or float(load) <= 0.0) and (pv_val > 0 or float(grid or 0) != 0):
                computed_load = round(pv_val + float(grid or 0.0) + bat_val, 1)
                load = max(0.0, computed_load)

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
        Fragt die Live-Telemetrie von der offiziellen Sungrow OpenAPI ab.
        """
        res = self.test_connection(credentials)
        if res.status == "success":
            return self.parse_payload(res.raw_sample)
        raise ValueError(res.error or res.message)

    def test_connection(self, credentials: Dict[str, Any]) -> AdapterTestResult:
        """
        Führt einen Verbindungstest gegen die offizielle Sungrow OpenAPI durch (OAuth2 / Token-basiert).
        """
        base_url = credentials.get("base_url") or getattr(settings, "SUNGROW_GATEWAY_URL", "https://gateway.isolarcloud.eu")
        appkey = credentials.get("appkey") or getattr(settings, "SUNGROW_APPKEY", "") or os.getenv("SUNGROW_APPKEY", "")
        app_secret = getattr(settings, "SUNGROW_APP_SECRET", "") or os.getenv("SUNGROW_APP_SECRET", "")
        token = credentials.get("token")
        ps_id = credentials.get("ps_id") or credentials.get("ps_ids") or ""
        if (not ps_id or str(ps_id) in ("default_ps", "12345", "")) and credentials.get("auth_ps_list") and isinstance(credentials["auth_ps_list"], list) and credentials["auth_ps_list"]:
            ps_id = str(credentials["auth_ps_list"][0])
            credentials["ps_id"] = ps_id

        # Sandbox- / Simulator-Modus prüfen
        is_mock = (
            bool(credentials.get("is_mock"))
            or str(appkey).lower() in ("mock", "fake", "demo", "test")
            or not credentials
            or (not appkey and not token and not credentials.get("auth_code"))
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

        redir_url = (
            credentials.get("redirect_uri")
            or credentials.get("redirect_url")
            or getattr(settings, "SUNGROW_REDIRECT_URL", "")
            or getattr(settings, "SUNGROW_REDIRECT_URI", "")
            or os.getenv("SUNGROW_REDIRECT_URL", "https://sharegy.de/api/v1/integrations/sungrow/callback")
        )

        gateway_list = ["https://gateway.isolarcloud.eu"]
        if base_url and base_url.rstrip("/") not in gateway_list:
            gateway_list.insert(0, base_url.rstrip("/"))

        def _extract_token_from_response(rj: Any) -> Optional[str]:
            if not isinstance(rj, dict):
                return None
            for k in ("token", "access_token", "accessToken", "app_token", "token_value", "tokenValue", "auth_token"):
                v = rj.get(k)
                if isinstance(v, str) and len(v.strip()) > 5:
                    return v.strip()
            for sub in ("result_data", "data", "resultData", "result"):
                rd = rj.get(sub)
                if isinstance(rd, str) and len(rd.strip()) > 5:
                    return rd.strip()
                if isinstance(rd, dict):
                    for k in ("token", "access_token", "accessToken", "app_token", "token_value", "tokenValue", "auth_token", "ticket"):
                        v = rd.get(k)
                        if isinstance(v, str) and len(v.strip()) > 5:
                            return v.strip()
            return None

        refresh_attempted = False

        def _refresh_openapi_token() -> bool:
            nonlocal token, refresh_attempted
            if refresh_attempted:
                return False
            refresh_attempted = True
            r_token = credentials.get("refresh_token")

            if r_token:
                for gw in gateway_list:
                    try:
                        r_resp = requests.post(
                            f"{gw}/openapi/apiManage/refreshToken",
                            json={
                                "appkey": appkey,
                                "refresh_token": r_token,
                            },
                            headers={"sys_code": "901", "x-access-key": app_secret, "Content-Type": "application/json"},
                            timeout=5,
                        )
                        logger.info("[SUNGROW_OPENAPI] apiManage/refreshToken on %s [%s]: %s", gw, r_resp.status_code, r_resp.text[:300])
                        if r_resp.status_code == 200:
                            rj = r_resp.json()
                            nt = _extract_token_from_response(rj)
                            if nt:
                                token = nt
                                credentials["token"] = token
                                rd = rj.get("result_data") or rj.get("data")
                                if isinstance(rd, dict) and rd.get("refresh_token"):
                                    credentials["refresh_token"] = rd["refresh_token"]
                                elif rj.get("refresh_token"):
                                    credentials["refresh_token"] = rj["refresh_token"]
                                logger.info("[SUNGROW_OPENAPI] Token successfully refreshed via %s/openapi/apiManage/refreshToken", gw)
                                return True
                    except Exception as e:
                        logger.debug("apiManage/refreshToken on %s failed: %s", gw, e)

            return False

        def _post_with_auth(endpoint: str, json_data: dict) -> Optional[requests.Response]:
            nonlocal token
            payload = dict(json_data)
            if appkey and "appkey" not in payload:
                payload["appkey"] = appkey
            if "lang" not in payload:
                payload["lang"] = "_de_DE"

            for gw in gateway_list:
                url = f"{gw}/{endpoint.lstrip('/')}"
                headers = {
                    "sys_code": "901",
                    "x-access-key": app_secret,
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
                try:
                    resp = requests.post(url, json=payload, headers=headers, timeout=4)
                    is_auth_err = resp.status_code in (401, 403)
                    if resp.status_code == 200:
                        try:
                            body = resp.json()
                            code_str = str(body.get("result_code", ""))
                            msg_str = str(body.get("result_msg", "")).lower()
                            if code_str in ("E00003", "E900", "E00000", "E911", "E912", "E914", "401", "403") or ("token" in msg_str and ("invalid" in msg_str or "expired" in msg_str)):
                                is_auth_err = True
                        except Exception:
                            pass

                    if is_auth_err:
                        logger.info("[SUNGROW_OPENAPI] Auth error on %s, attempting automatic token refresh...", url)
                        if _refresh_openapi_token():
                            headers["Authorization"] = f"Bearer {token}"
                            resp = requests.post(url, json=payload, headers=headers, timeout=4)
                            if resp.status_code == 200:
                                return resp
                    elif resp.status_code == 200:
                        return resp
                except Exception as req_err:
                    logger.debug("Sungrow request to %s failed: %s", url, req_err)

            return None

        # 1. Automatischer Auth-Code Austausch bei Neu-Kopplung
        if credentials.get("auth_code") and not token:
            for gw in gateway_list:
                try:
                    t_resp = requests.post(
                        f"{gw}/openapi/apiManage/token",
                        json={
                            "appkey": appkey,
                            "code": credentials["auth_code"],
                            "grant_type": "authorization_code",
                            "redirect_uri": redir_url,
                        },
                        headers={"sys_code": "901", "x-access-key": app_secret, "Content-Type": "application/json"},
                        timeout=5,
                    )
                    if t_resp.status_code == 200:
                        t_cand = t_resp.json().get("access_token") or t_resp.json().get("token")
                        if not t_cand and isinstance(t_resp.json().get("result_data"), dict):
                            t_cand = t_resp.json()["result_data"].get("access_token") or t_resp.json()["result_data"].get("token")
                        if t_cand:
                            token = t_cand
                            credentials["token"] = token
                            if t_resp.json().get("refresh_token"):
                                credentials["refresh_token"] = t_resp.json()["refresh_token"]
                            elif isinstance(t_resp.json().get("result_data"), dict) and t_resp.json()["result_data"].get("refresh_token"):
                                credentials["refresh_token"] = t_resp.json()["result_data"]["refresh_token"]
                            break
                except Exception as ex_err:
                    logger.debug("Auto token exchange failed on %s: %s", gw, ex_err)

        if not token:
            # Letzter Versuch: Token via Developer Refresh
            if not _refresh_openapi_token():
                err_msg = "Kein gültiger Sungrow OpenAPI Token vorhanden. Bitte autorisiere die Anlage über 'iSolarCloud 1-Klick verbinden'."
                return AdapterTestResult(status="error", error=err_msg, message=err_msg)

        # 2. Automatische Anlagen-ID (ps_id) Erkennung über offizielle OpenAPI
        if not ps_id or str(ps_id) in ("default_ps", "12345", ""):
            try:
                list_resp = _post_with_auth("openapi/platform/queryPowerStationList", {"page": 1, "size": 100, "lang": "_de_DE"})
                if list_resp and list_resp.status_code == 200:
                    list_json = list_resp.json()
                    list_data = list_json.get("result_data") or list_json.get("data") or {}
                    if isinstance(list_data, dict):
                        stations = list_data.get("pageList") or list_data.get("data_list") or []
                        if stations and isinstance(stations, list) and len(stations) > 0:
                            first_st = stations[0]
                            if isinstance(first_st, dict):
                                ps_id = str(first_st.get("ps_id") or first_st.get("id") or first_st.get("ps_key") or "")
                                credentials["ps_id"] = ps_id
                                credentials["ps_name"] = first_st.get("ps_name") or first_st.get("name", "Sungrow PV-Anlage")
                                logger.info("[SUNGROW_OPENAPI] Auto-discovered plant ps_id: %s (%s)", ps_id, credentials["ps_name"])
            except Exception as e:
                logger.debug("Fetch ps_id via platform query failed: %s", e)

        raw_data: Dict[str, Any] = {"result_code": "1", "result_data": {}}

        # 3. Echtzeit-Messpunkte abfragen (getPowerStationRealTimeData / getDeviceRealTimeData)
        try:
            ps_id_str = str(ps_id) if ps_id and str(ps_id) not in ("default_ps", "") else ""
            ps_list = [ps_id_str] if ps_id_str else []
            
            rt_endpoints = [
                ("openapi/platform/getPowerStationRealTimeData", {
                    "ps_id_list": ps_list,
                    "point_id_list": self.MEASURE_POINTS,
                    "is_get_point_dict": "1",
                    "lang": "_de_DE",
                }),
                ("openapi/platform/getDeviceRealTimeData", {
                    "device_type": 11,
                    "ps_key_list": [f"{ps_id_str}_11_0_0"] if ps_id_str else [],
                    "point_id_list": self.MEASURE_POINTS,
                    "lang": "_de_DE",
                }),
            ]

            rt_resp = None
            for ep_name, ep_payload in rt_endpoints:
                resp = _post_with_auth(ep_name, ep_payload)
                if resp and resp.status_code == 200:
                    rj = resp.json()
                    rd = rj.get("result_data") or rj.get("data")
                    if rd and isinstance(rd, dict) and (rd.get("device_point_list") or rd.get("point_dict")):
                        rt_resp = resp
                        logger.info("[SUNGROW_OPENAPI] Received live points from %s", ep_name)
                        break

            if rt_resp and rt_resp.status_code == 200:
                rt_json = rt_resp.json()
                rt_res_data = rt_json.get("result_data") or rt_json.get("data") or {}
                if isinstance(rt_res_data, dict):
                    point_dict = rt_res_data.get("point_dict") or {}
                    if point_dict:
                        logger.info("[SUNGROW_OPENAPI] Discovered Point Dictionary: %s", point_dict)
                    pts = rt_res_data.get("device_point_list") or []
                    if pts:
                        p_data = {}
                        for item in pts:
                            if isinstance(item, dict):
                                pt_item = item.get("device_point") or item
                                if isinstance(pt_item, dict):
                                    if "point_id" in pt_item and "point_value" in pt_item:
                                        pid = str(pt_item["point_id"])
                                        p_data[pid] = pt_item["point_value"]
                                        p_data[f"p{pid}"] = pt_item["point_value"]
                                    else:
                                        for k, v in pt_item.items():
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

                        def _get_pt_pos(*keys):
                            for k in keys:
                                for variant in [str(k), f"p{k}", f"P{k}"]:
                                    if variant in p_data and p_data[variant] is not None:
                                        try:
                                            v = float(p_data[variant])
                                            if v > 0.0:
                                                return v
                                        except (ValueError, TypeError):
                                            pass
                            return None

                        # PV Power: Prüfe Haupt-Messpunkte sowie String- & MPPT-Summen
                        pv_direct = _get_pt_pos("83067", "83329", "83033", "83002", "83020", "83006")
                        mppt1 = _get_pt_pos("83011") or 0.0
                        mppt2 = _get_pt_pos("83012") or 0.0
                        mppt3 = _get_pt_pos("83046") or 0.0
                        mppt_sum = mppt1 + mppt2 + mppt3

                        str1 = _get_pt_pos("83016") or 0.0
                        str2 = _get_pt_pos("83017") or 0.0
                        str3 = _get_pt_pos("83018") or 0.0
                        str_sum = str1 + str2 + str3

                        pv_candidates = [v for v in [pv_direct, mppt_sum if mppt_sum > 0 else None, str_sum if str_sum > 0 else None, _get_pt("83067", "83329", "83033", "83002")] if v is not None]
                        pv = max(pv_candidates) if pv_candidates else 0.0
                        load = _get_pt("83052", "83330", "83106") or 0.0
                        grid = _get_pt("83549", "83328", "83032", "83051") or 0.0
                        bat_pwr = _get_pt("83238", "83326", "83104", "83111", "83112") or 0.0
                        soc_raw = _get_pt("83129", "83252", "83334", "83232")

                        soc_val = None
                        if soc_raw is not None:
                            if 0.0 <= soc_raw <= 1.0:
                                soc_val = round(soc_raw * 100.0, 1)
                            else:
                                soc_val = round(soc_raw, 1)

                        # 1. Batterie Leistung & Richtung plausibilisieren
                        if abs(bat_pwr) < 1.0 and soc_val is not None:
                            # Wenn Sungrow keinen direkten Batterieleistungswert meldet, aus Bilanz ableiten:
                            deficit = load - pv - max(0.0, grid)
                            if deficit > 10.0 and soc_val > 5.0:
                                bat_pwr = round(deficit, 1)  # Positiv = Entladen (Discharge ins Haus)
                            elif (pv - load + min(0.0, grid)) > 10.0 and soc_val < 98.0:
                                surplus = pv - load + min(0.0, grid)
                                bat_pwr = -round(surplus, 1)  # Negativ = Laden (Charge aus PV)
                        elif soc_val is not None:
                            if soc_val >= 98.0 and bat_pwr < 0:
                                bat_pwr = 0.0
                            elif soc_val <= 5.0 and bat_pwr > 0:
                                bat_pwr = 0.0

                        # 2. Netzeinspeisung / Grid Plausibilisierung vorzeichengenau:
                        # Negativ = Netzeinspeisung (Export), Positiv = Netzbezug (Import)
                        bat_charge = abs(min(0.0, bat_pwr))
                        bat_discharge = max(0.0, bat_pwr)

                        if pv > 50.0:
                            surplus = pv + bat_discharge - load - bat_charge
                            if surplus > 15.0:
                                if grid > 0:
                                    grid = -abs(grid)
                                elif grid == 0.0:
                                    grid = -round(surplus, 1)
                            elif load > (pv + bat_discharge + 15.0):
                                if grid < 0:
                                    grid = abs(grid)

                        if load <= 0.0 or (pv > 50.0 and abs(load - pv) < 5.0):
                            load = max(0.0, round(pv + grid + bat_pwr, 1))

                        today_kwh = _get_pt("83022", "83331", "83009", "83072", "83119", "83013", "83021", "83049", "83050", "83012")
                        if today_kwh is None:
                            res_d = raw_data.get("result_data", {})
                            if isinstance(res_d, dict):
                                today_kwh = res_d.get("today_energy") or res_d.get("todayEnergy") or res_d.get("today_yield") or res_d.get("eToday")
                        if today_kwh is not None:
                            try:
                                today_kwh = float(today_kwh)
                                if today_kwh > 1000.0:
                                    today_kwh = today_kwh / 1000.0
                            except (ValueError, TypeError):
                                today_kwh = None

                        raw_data["_direct_metrics"] = {
                            "pv_power_w": max(0.0, round(pv, 1)),
                            "load_power_w": max(0.0, round(load, 1)),
                            "grid_power_w": round(grid, 1),
                            "battery_power_w": round(bat_pwr, 1),
                            "battery_soc": soc_val,
                            "daily_generation_kwh": today_kwh,
                        }
        except Exception as e:
            logger.warning("getPowerStationRealTimeData / getDeviceRealTimeData query failed: %s", e)

        # 4. Details abfragen als Ergänzung (getPowerStationDetail)
        if ps_id and str(ps_id) not in ("default_ps", ""):
            try:
                resp = _post_with_auth("openapi/platform/getPowerStationDetail", {"ps_ids": str(ps_id), "lang": "_de_DE"})
                if resp and resp.status_code == 200:
                    det_json = resp.json()
                    det_res_data = det_json.get("result_data") or det_json.get("data") or {}
                    if isinstance(det_res_data, dict):
                        if det_res_data.get("data_list") and isinstance(det_res_data["data_list"], list) and det_res_data["data_list"]:
                            raw_data["result_data"].update(det_res_data["data_list"][0])
                        elif "ps_id" in det_res_data or "curr_power" in det_res_data:
                            raw_data["result_data"].update(det_res_data)
            except Exception as e:
                logger.debug("getPowerStationDetail failed: %s", e)

        telemetry = self.parse_payload(raw_data)

        # Validitätsprüfung
        if "_direct_metrics" not in raw_data and not raw_data.get("result_data"):
            err_msg = "Sungrow OpenAPI-Sitzung ist abgelaufen oder ungültig. Bitte Autorisierung über 'iSolarCloud 1-Klick verbinden' erneuern."
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
            message=f"Live-Verbindung zu {self.name} (OpenAPI) erfolgreich!",
            live_metrics=telemetry.to_metrics_dict(),
            raw_sample=raw_data,
            simulated=False,
        )
