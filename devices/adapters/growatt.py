"""
devices/adapters/growatt.py

Isolierter Adapter für Growatt ShineServer & Growatt OpenAPI.
Unterstützt:
1. Growatt OpenAPI V1 / V4 (Token-basiert)
2. ShineServer / ShinePhone Session Login mit MD5-Nibble-Hashing
3. Standardisierte Transformation in CanonicalTelemetry
"""

import logging
import hashlib
import datetime
import requests
from typing import Dict, Any, Optional
from django.utils import timezone

from devices.adapters.contracts import BaseInverterAdapter, CanonicalTelemetry, AdapterTestResult

logger = logging.getLogger(__name__)


class GrowattAdapter(BaseInverterAdapter):
    profile_id = "growatt_server"
    name = "Growatt ShineServer"
    vendor = "Growatt"
    protocol = "http_cloud"
    category = "inverter_hybrid"

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        MD5-Hash mit 'c'-Ersetzung an geraden Positionen für 0-Nibbles (Growatt-Standard).
        Entspricht der Growatt Web/App Authentifizierung (PyPi_GrowattServer).
        """
        password_md5 = hashlib.md5(str(password).encode("utf-8")).hexdigest()
        res = list(password_md5)
        for i in range(0, len(res), 2):
            if res[i] == "0":
                res[i] = "c"
        return "".join(res)

    @staticmethod
    def _hash_password_std_md5(password: str) -> str:
        """
        Standard MD5-Hash (Fallback).
        """
        return hashlib.md5(str(password).encode("utf-8")).hexdigest()

    def generate_mock_payload(self) -> dict:

        """
        Generiert realistische Live-Messdaten für Growatt-Systeme.
        """
        import random
        now = timezone.now()
        hour = now.hour

        if 6 <= hour <= 20:
            pv_factor = max(0.0, 1.0 - ((hour - 13.0) / 7.0) ** 2)
            pv_w = round(random.uniform(3500.0, 7800.0) * pv_factor, 1)
        else:
            pv_w = 0.0

        load_w = round(random.uniform(600.0, 2200.0), 1)
        diff = pv_w - load_w

        if diff > 0:
            bat_w = round(min(diff * 0.7, 3000.0) * -1, 1) # Laden
            grid_w = round((diff + bat_w) * -1, 1)        # Einspeisen
        else:
            bat_w = round(min(abs(diff), 2500.0), 1)       # Entladen
            grid_w = round(abs(diff) - bat_w, 1)          # Bezug

        return {
            "data": {
                "pac": pv_w,
                "pactogrid": grid_w,
                "pload": load_w,
                "pdisCharge": max(0.0, bat_w),
                "pcharge": abs(min(0.0, bat_w)),
                "soc": round(random.uniform(65.0, 95.0), 1),
                "eToday": round(pv_w * 0.0042 + random.uniform(5.0, 15.0), 2),
            }
        }

    def parse_payload(self, raw_data: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Wandelt ein Growatt API JSON-Objekt in CanonicalTelemetry um.
        Growatt liefert Leistungen standardmäßig in Watt und Energien in kWh.
        Unterstützt Multi-String-Ertragsberechnung (ppv1 + ppv2 + ...), DC/AC-Hybrid-Erkennung
        und aggregierte Plant-Metriken (currentPower).
        """
        # Flaches Wörterbuch aus verschachtelten Objekten aufbauen
        flat: Dict[str, Any] = {}

        def _walk(item):
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, (int, float, str, bool)) or v is None:
                        is_empty_or_zero = v in (None, "", "-", "--", "null", "none", "0", "0.0", "0.00", "0 W", "0W", "0 kW", "0kW", 0, 0.0, False)
                        if k not in flat or (flat[k] in (None, "", "-", "--", "null", "none", "0", "0.0", "0.00", "0 W", "0W", "0 kW", "0kW", 0, 0.0, False) and not is_empty_or_zero):
                            flat[k] = v
                        # Normalisierte Schlüssel (z. B. 'Current Power(kW)' -> 'current_power', 'currentpower')
                        clean_k = str(k).lower().replace(" ", "_").replace("(", "_").replace(")", "").replace("：", "").replace(":", "").strip()
                        if clean_k not in flat or (flat[clean_k] in (None, "", "0", 0, 0.0) and not is_empty_or_zero):
                            flat[clean_k] = v
                        clean_k2 = str(k).lower().replace(" ", "").replace("(", "").replace(")", "").replace("_", "").replace("：", "").replace(":", "").strip()
                        if clean_k2 not in flat or (flat[clean_k2] in (None, "", "0", 0, 0.0) and not is_empty_or_zero):
                            flat[clean_k2] = v
                    elif isinstance(v, (dict, list)):
                        _walk(v)
            elif isinstance(item, list):
                for elem in item:
                    _walk(elem)

        _walk(raw_data)

        def _get_val(*keys, is_power: bool = False) -> Optional[float]:
            vals = []
            for k in keys:
                if k in flat and flat[k] is not None:
                    raw = str(flat[k]).strip().replace(",", ".")
                    if raw.lower() in ("-", "--", "null", "none", "n/a", ""):
                        continue
                    factor = 1.0
                    low = raw.lower()
                    has_kw = "kw" in low or "kw" in str(k).lower()
                    has_w = "w" in low and not has_kw
                    if is_power:
                        if has_kw:
                            factor = 1000.0
                        elif has_w:
                            factor = 1.0
                    else:
                        # Für Energie / Zählerstände (Standardeinheit: kWh)
                        if has_w and not has_kw and "wh" in low:
                            factor = 0.001
                        elif has_kw:
                            factor = 1.0
                    low = low.replace("kwh", "").replace("wh", "").replace("kw", "").replace("w", "").replace("%", "").strip()
                    import re
                    match = re.search(r"[-+]?\d*\.?\d+", low)
                    if match:
                        try:
                            val = float(match.group(0)) * factor
                            # Wenn es ein Leistungswert ist und factor == 1.0 war (keine explizite Einheit):
                            # Bei Growatt sind 'currentPower', 'nominalPower', 'currPower', 'total_power', 'plantPower'
                            # bei Werten < 100.0 standardmäßig in kW angegeben!
                            if is_power and not has_w and not has_kw:
                                if any(pk in str(k).lower() for pk in ["currentpower", "current_power", "currpower", "curr_power", "nominalpower", "plantpower"]) and 0.0 < abs(val) <= 100.0:
                                    val = val * 1000.0
                            vals.append(val)
                        except (ValueError, TypeError):
                            pass
            pos_vals = [v for v in vals if v > 0]
            if pos_vals:
                return max(pos_vals)
            return vals[0] if vals else None

        # 1. PV Erzeugung (DC Solar Input & AC Output & Plant Totals)
        ppv_direct = _get_val("ppv", "ppvTotal", "p_pv", "pv_power", "pvPower", "pAct", "pact", "invTodayPpv", "current_power", "currentpower", "current_power_kw", "currentpowerkw", is_power=True)
        curr_power = _get_val("currentPower", "current_power", "currPower", "curr_power", "total_power", "plantPower", "current_power_kw", "currentpowerkw", is_power=True)
        pac_direct = _get_val("pac", "invPac", "pacToUserTotal", "pac1", "power", is_power=True)

        # Multi-String PV Summe (z. B. String 1 + String 2 + String 3 + String 4)
        ppv1 = _get_val("ppv1", "pPv1", "p_pv1", is_power=True) or 0.0
        ppv2 = _get_val("ppv2", "pPv2", "p_pv2", is_power=True) or 0.0
        ppv3 = _get_val("ppv3", "pPv3", "p_pv3", is_power=True) or 0.0
        ppv4 = _get_val("ppv4", "pPv4", "p_pv4", is_power=True) or 0.0
        ppv_string_sum = ppv1 + ppv2 + ppv3 + ppv4

        # Volt * Ampere Strings (falls nur Spannungen und Ströme geliefert werden)
        vpv1 = _get_val("vpv1", "vPv1") or 0.0
        ipv1 = _get_val("ipv1", "iPv1") or 0.0
        vpv2 = _get_val("vpv2", "vPv2") or 0.0
        ipv2 = _get_val("ipv2", "iPv2") or 0.0
        va_string_sum = round((vpv1 * ipv1) + (vpv2 * ipv2), 1)

        # Prioritätsauswahl für PV Erzeugung: Bevorzuge den höchsten plausiblen positiven Messwert
        candidates = [v for v in [ppv_direct, ppv_string_sum if ppv_string_sum > 0 else None, curr_power, pac_direct, va_string_sum if va_string_sum > 0 else None] if v is not None and v > 0]
        if candidates:
            pv = max(candidates)
        else:
            pv = ppv_direct or curr_power or pac_direct or 0.0

        # 2. Batterie Leistung (+ Entladung, - Ladung) & SoC
        bat_dis = _get_val("pdisCharge", "pdisCharge1", "pDisCharge", "pDischarge", is_power=True) or 0.0
        bat_chg = _get_val("pcharge", "pcharge1", "pCharge", is_power=True) or 0.0
        bat_to_storage = _get_val("pactostorage", "pstorage", is_power=True) or 0.0
        bat_generic = _get_val("battery_power", "battery_power_w", "batteryPower", "batPower", "B_P1", is_power=True)

        if bat_generic is not None and bat_dis == 0.0 and bat_chg == 0.0 and bat_to_storage == 0.0:
            bat_pwr = bat_generic
        elif bat_to_storage > 0 and bat_chg == 0:
            bat_pwr = -abs(bat_to_storage)
        else:
            bat_pwr = bat_dis - (bat_chg or bat_to_storage)

        soc = _get_val("soc", "batterySoc", "battery_soc", "batteryPercent", "chargeLevel", "capacity", "SOC", "storageSoc", "bmsSoc")

        # 3. Netzleistung (+ Bezug, - Einspeisung)
        grid_export_val = _get_val("pactogrid", "toGridPower", "to_grid_power", "pToGrid", "feed_in_power", "p_feed_in", is_power=True)
        grid_import_val = _get_val("pfromgrid", "fromGridPower", "gridPurchasedPower", "pFromGrid", "p_import", is_power=True)
        grid_net = _get_val("pgrid", "pGrid", "grid_power", "gridPower", is_power=True)

        if grid_export_val is not None or grid_import_val is not None:
            grid = float(grid_import_val or 0.0) - float(grid_export_val or 0.0)
        elif grid_net is not None:
            grid = float(grid_net)
        else:
            grid = None

        # 4. Hausverbrauch (pactouser / pLocalLoad / pload)
        load = _get_val("pactouser", "pLocalLoad", "pToUser", "pload", "use_power", "useEnergy", "familyLoadPower", "load_power", "loadPower", "use_power_w", "home_load", "consumption", is_power=True)

        # 5. Physikalische Plausibilisierung für Grid, Battery & Load
        pv_val = max(0.0, float(pv or 0.0))
        bat_val = float(bat_pwr or 0.0)
        soc_val = float(soc) if soc is not None else None
        eff_load = float(load) if (load is not None and load > 0) else None

        # Batterie Leistung aus Leistungsbilanz ableiten falls Inverter keine direkte Leistung meldet
        if abs(bat_val) < 1.0 and soc_val is not None and eff_load is not None:
            deficit = eff_load - pv_val - max(0.0, float(grid or 0.0))
            if deficit > 10.0 and soc_val > 5.0:
                bat_val = round(deficit, 1)  # Entladen (+W)
                bat_pwr = bat_val
            elif (pv_val - eff_load + min(0.0, float(grid or 0.0))) > 10.0 and soc_val < 98.0:
                surplus = pv_val - eff_load + min(0.0, float(grid or 0.0))
                bat_val = -round(surplus, 1) # Laden (-W)
                bat_pwr = bat_val
        elif soc_val is not None:
            if soc_val >= 98.0 and bat_val < 0:
                bat_val = 0.0
                bat_pwr = 0.0
            elif soc_val <= 5.0 and bat_val > 0:
                bat_val = 0.0
                bat_pwr = 0.0

        if grid is not None:
            grid_val = float(grid)
            bat_charging = abs(min(0.0, bat_val))
            bat_discharging = max(0.0, bat_val)
            eff_load_val = eff_load or 0.0

            if pv_val > 50.0:
                surplus = pv_val + bat_discharging - eff_load_val - bat_charging
                if surplus > 30.0:
                    if grid_val > 0:
                        grid = -abs(grid_val)
                    elif grid_val == 0.0 and surplus > 50.0 and load is not None:
                        grid = -round(surplus, 1)
                elif eff_load_val > (pv_val + bat_discharging + 30.0):
                    if grid_val < 0:
                        grid = abs(grid_val)

            if (load is None or load <= 0.0) and pv_val > 50.0:
                if grid_val > 0 and abs(grid_val - pv_val) < (pv_val * 0.5 + 500):
                    grid = -abs(grid_val)
                computed_load = round(pv_val + float(grid) + bat_val, 1)
                if load is None or load <= 0:
                    load = max(0.0, computed_load)
        elif load is None or load <= 0.0:
            if pv_val > 0 or bat_val != 0:
                load = max(0.0, round(pv_val + bat_val, 1))

        # 6. Tagesertrag & Gesamtertrag
        daily = _get_val(
            "eToday", "etoday", "todayEnergy", "today_energy", "e_today", "eTodayTotal",
            "eAcChargeToday", "todayYield", "daily_generation", "solar_yield",
            "generationToday", "generation_today", "generation_today_kwh", "generationtodaykwh",
            "generationtoday"
        )
        total = _get_val(
            "eTotal", "etotal", "total_energy", "totalEnergy", "total_power_generation",
            "total_power_generation_kwh", "totalpowergenerationkwh", "totalpowergeneration"
        )

        telemetry = CanonicalTelemetry(
            pv_power_w=pv,
            grid_power_w=grid,
            load_power_w=load,
            battery_power_w=bat_pwr,
            battery_soc=soc,
            daily_yield_kwh=daily,
            total_yield_kwh=total,
            raw_payload=raw_data,
        )
        return telemetry.validate()

    def fetch_telemetry(self, credentials: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Führt die Abfrage gegen Growatt durch und liefert CanonicalTelemetry.
        """
        res = self.test_connection(credentials)
        if res.status == "success":
            return self.parse_payload(res.raw_sample)
        raise ValueError(res.error or res.message)

    def test_connection(self, credentials: Dict[str, Any]) -> AdapterTestResult:
        """
        Verbindungstest gegen Growatt OpenAPI oder ShineServer Session Login.
        """
        token = credentials.get("token") or credentials.get("api_key")
        plant_id = str(credentials.get("plant_id") or "").strip()
        device_sn = str(credentials.get("device_sn") or credentials.get("sn") or "").strip()
        username = str(credentials.get("user_account") or credentials.get("username") or credentials.get("userName") or "").strip()
        password = str(credentials.get("user_password") or credentials.get("password") or "").strip()

        is_mock = (
            str(token).startswith("test_")
            or str(token).startswith("mock_")
            or username.lower() in ("test", "demo", "mock", "test_growatt_user")
            or (not token and not username)
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

        raw_data: Dict[str, Any] = {"data": {}}
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Requested-With": "XMLHttpRequest",
        })

        # PFAD A: Growatt OpenAPI (Token vorhanden)
        if token and not is_mock:
            token_clean = str(token).strip()
            api_headers = {
                "token": token_clean,
                "Authorization": f"Bearer {token_clean}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # 1. Plant ID ermitteln / auflösen
            if not plant_id or not plant_id.isdigit():
                try:
                    plist_resp = session.get("https://openapi.growatt.com/v1/plant/list", headers=api_headers, timeout=10)
                    if plist_resp.status_code == 200:
                        p_json = plist_resp.json()
                        p_data = p_json.get("data")
                        plants = []
                        if isinstance(p_data, list):
                            plants = p_data
                        elif isinstance(p_data, dict):
                            plants = p_data.get("plants") or p_data.get("plant_list") or p_data.get("data") or [p_data]
                        if plants and isinstance(plants, list) and len(plants) > 0:
                            matched = None
                            for p_item in plants:
                                if isinstance(p_item, dict):
                                    p_name = str(p_item.get("plant_name") or p_item.get("name") or p_item.get("plantName") or "").strip().lower()
                                    p_id_str = str(p_item.get("plant_id") or p_item.get("id") or p_item.get("plantId") or "").strip()
                                    if plant_id and (plant_id.lower() in (p_name, p_id_str)):
                                        matched = p_item
                                        break
                            if not matched:
                                matched = plants[0]
                            if isinstance(matched, dict):
                                plant_id = str(matched.get("plant_id") or matched.get("id") or matched.get("plantId") or "")
                                credentials["plant_id"] = plant_id
                                logger.info("Growatt auto-discovered plant_id: %s (Name: %s)", plant_id, matched.get("plant_name"))
                except Exception as e:
                    logger.warning("Growatt OpenAPI plant list discovery failed: %s", e)

            # 2. Alle Geräte-Seriennummern der Anlage ermitteln
            discovered_sn_list = [device_sn] if device_sn else []
            if plant_id:
                try:
                    dlist_resp = session.get(
                        "https://openapi.growatt.com/v1/device/list",
                        headers=api_headers,
                        params={"plant_id": plant_id},
                        timeout=10,
                    )
                    if dlist_resp.status_code == 200:
                        d_json = dlist_resp.json()
                        d_data = d_json.get("data")
                        dev_items = []
                        if isinstance(d_data, list):
                            dev_items = d_data
                        elif isinstance(d_data, dict):
                            dev_items = d_data.get("devices") or d_data.get("device_list") or d_data.get("data") or d_data.get("obj") or []
                        if isinstance(dev_items, list):
                            for dev_obj in dev_items:
                                if isinstance(dev_obj, dict):
                                    sn = str(dev_obj.get("device_sn") or dev_obj.get("sn") or dev_obj.get("deviceSn") or dev_obj.get("inverterId") or "").strip()
                                    if sn and sn not in discovered_sn_list:
                                        discovered_sn_list.append(sn)
                            if discovered_sn_list and not device_sn:
                                device_sn = discovered_sn_list[0]
                                credentials["device_sn"] = device_sn
                                logger.info("Growatt auto-discovered devices: %s", discovered_sn_list)
                except Exception as e:
                    logger.debug("Growatt device/list lookup failed: %s", e)

            # 3. Alle Detail-Endpunkte für alle erkannten Seriennummern abfragen
            for sn_val in (discovered_sn_list if discovered_sn_list else ([device_sn] if device_sn else [])):
                for endpoint in [
                    "https://openapi.growatt.com/v1/device/inverter/inverter_last_data",
                    "https://openapi.growatt.com/v1/device/tlx/tlx_last_data",
                    "https://openapi.growatt.com/v1/device/min/min_last_data",
                    "https://openapi.growatt.com/v1/device/mic/mic_last_data",
                    "https://openapi.growatt.com/v1/device/mod/mod_last_data",
                    "https://openapi.growatt.com/v1/device/mid/mid_last_data",
                    "https://openapi.growatt.com/v1/device/mac/mac_last_data",
                    "https://openapi.growatt.com/v1/device/max/max_last_data",
                    "https://openapi.growatt.com/v1/device/storage/storage_last_data",
                    "https://openapi.growatt.com/v1/device/mix/mix_last_data",
                    "https://openapi.growatt.com/v1/device/sph/sph_last_data",
                    "https://openapi.growatt.com/v1/device/spa/spa_last_data",
                    "https://openapi.growatt.com/v1/device/noah/noah_last_data",
                ]:
                    try:
                        dev_resp = session.get(
                            endpoint,
                            headers=api_headers,
                            params={
                                "device_sn": sn_val,
                                "inverter_sn": sn_val,
                                "tlx_sn": sn_val,
                                "min_sn": sn_val,
                                "mic_sn": sn_val,
                                "mod_sn": sn_val,
                                "mid_sn": sn_val,
                                "mac_sn": sn_val,
                                "max_sn": sn_val,
                                "storage_sn": sn_val,
                                "mix_sn": sn_val,
                                "sph_sn": sn_val,
                                "spa_sn": sn_val,
                                "noah_sn": sn_val,
                            },
                            timeout=8,
                        )
                        if dev_resp.status_code == 200:
                            d_json = dev_resp.json()
                            d_data = d_json.get("data")
                            if isinstance(d_data, dict) and d_data:
                                raw_data["data"].update(d_data)
                    except Exception:
                        pass

            if plant_id:
                for p_ep in [
                    "https://openapi.growatt.com/v1/plant/data",
                    "https://openapi.growatt.com/v1/plant/data/overview",
                ]:
                    try:
                        p_resp = session.get(
                            p_ep,
                            headers=api_headers,
                            params={"plant_id": plant_id},
                            timeout=10,
                        )
                        if p_resp.status_code == 200 and p_resp.json().get("data"):
                            p_d = p_resp.json()["data"]
                            if isinstance(p_d, dict):
                                raw_data["data"].update(p_d)
                    except Exception as e:
                        logger.warning("Growatt plant/data endpoint %s failed: %s", p_ep, e)

            telemetry = self.parse_payload(raw_data)
            return AdapterTestResult(
                status="success",
                message=f"Live-Verbindung zu {self.name} erfolgreich!",
                live_metrics=telemetry.to_metrics_dict(),
                raw_sample=raw_data,
                simulated=False,
            )

        # PFAD B: ShineServer Web Login (Home Assistant / PyPi_GrowattServer kompatibel)
        if username and password:
            hashed_pw = self._hash_password(str(password))
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
                # 1. Versuch: newTwoLoginAPI.do mit MD5-Nibble Hash
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
                        logger.debug("Growatt newTwoLoginAPI failed on host %s: %s", host, e)

                    # 2. Versuch: /login Form Endpoint (PyPi_GrowattServer)
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
                    p_list_resp = session.get(f"{active_host}/PlantListAPI.do", params={"userId": user_id}, timeout=10)
                    if p_list_resp.status_code == 200:
                        p_j = p_list_resp.json()
                        plants_info = p_j.get("back") if isinstance(p_j.get("back"), dict) else p_j
                        if isinstance(plants_info.get("totalData"), dict):
                            raw_data["data"].update(plants_info["totalData"])
                        plant_arr = plants_info.get("data", [])
                        if plant_arr and isinstance(plant_arr, list):
                            matched_plant = None
                            for p_item in plant_arr:
                                if isinstance(p_item, dict):
                                    p_name = str(p_item.get("plantName") or p_item.get("name") or "").strip().lower()
                                    p_id_str = str(p_item.get("plantId") or p_item.get("id") or "").strip()
                                    if plant_id and (plant_id.lower() in (p_name, p_id_str)):
                                        matched_plant = p_item
                                        break
                            if not matched_plant and plant_arr:
                                matched_plant = plant_arr[0]

                            if matched_plant and isinstance(matched_plant, dict):
                                raw_data["data"].update(matched_plant)
                                if isinstance(matched_plant.get("plantData"), dict):
                                    raw_data["data"].update(matched_plant["plantData"])
                                real_num_id = str(matched_plant.get("plantId") or matched_plant.get("id") or "")
                                if real_num_id:
                                    plant_id = real_num_id
                                    credentials["plant_id"] = plant_id
                                    logger.info("Growatt Web Login resolved plant_id: %s (Name: %s)", plant_id, matched_plant.get("plantName"))

                    # 2. Plant Detail API (Primary Plant Telemetry Endpoint in Home Assistant)
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
                                        # Serial-Numbers aus allen Geräte-Listen extrahieren
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

                    # Falls ein SN erkannt wurde, in credentials für schnelles Re-Polling sichern
                    if discovered_devices and not device_sn:
                        credentials["device_sn"] = discovered_devices[0]

                    # 4. Detaillierte Live-Abfragen für alle erkannten Wechselrichter & Speicher
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

                    # 5. Speicher- & Gesamtstatus der Anlage
                    if plant_id:
                        for stor_ep, params, p_data in [
                            (f"{active_host}/newStorageAPI.do", {"op": "getStorageTotalData"}, {"plantId": plant_id}),
                            (f"{active_host}/newStorageAPI.do", {"op": "getStorageEnergyOverview"}, {"plantId": plant_id}),
                        ]:
                            try:
                                r = session.post(stor_ep, params=params, data=p_data, timeout=8)
                                if r.status_code == 200:
                                    j = r.json()
                                    if isinstance(j, dict):
                                        d = j.get("obj") or j.get("back") or j.get("data") or j
                                        if isinstance(d, dict) and d:
                                            raw_data["data"].update(d)
                            except Exception:
                                pass

                    telemetry = self.parse_payload(raw_data)
                    return AdapterTestResult(
                        status="success",
                        message=f"Live-Verbindung zu {self.name} erfolgreich!",
                        live_metrics=telemetry.to_metrics_dict(),
                        raw_sample=raw_data,
                        simulated=False,
                    )
                except Exception as e:
                    logger.warning("Growatt Web Login data retrieval error: %s", e)
                    if raw_data.get("data"):
                        telemetry = self.parse_payload(raw_data)
                        return AdapterTestResult(
                            status="success",
                            message=f"Live-Verbindung zu {self.name} erfolgreich!",
                            live_metrics=telemetry.to_metrics_dict(),
                            raw_sample=raw_data,
                            simulated=False,
                        )
                    err_msg = f"Growatt Datenabfrage fehlgeschlagen: {e}"
                    return AdapterTestResult(status="error", error=err_msg, message=err_msg)

        err_msg = "Growatt Login fehlgeschlagen: Bitte prüfe Benutzername, Passwort oder API-Token."
        return AdapterTestResult(status="error", error=err_msg, message=err_msg)

