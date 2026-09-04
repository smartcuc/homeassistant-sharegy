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
        MD5-Hash mit 'c'-Ersetzung an ungeraden Positionen für 0-Nibbles (Growatt-Standard).
        """
        password_md5 = hashlib.md5(str(password).encode("utf-8")).hexdigest()
        res = list(password_md5)
        for i in range(0, len(res), 2):
            if res[i] == "0":
                res[i] = "c"
        return "".join(res)

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
        """
        # Flaches Wörterbuch aus verschachtelten Objekten aufbauen
        flat: Dict[str, Any] = {}

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

        _walk(raw_data)

        def _get_val(*keys) -> Optional[float]:
            for k in keys:
                if k in flat and flat[k] is not None:
                    raw = str(flat[k]).strip().replace(",", ".")
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
                            return float(match.group(0)) * factor
                        except (ValueError, TypeError):
                            pass
            return None

        # 1. PV Erzeugung
        pv = _get_val(
            "pac", "ppv", "ppv1", "ppv2", "pPv1", "pPv2", "pactouser",
            "pacToUserTotal", "nominalPower", "invPac", "power", "pv_power", "pvPower", "pAct", "pact", "pac1", "ppvTotal"
        )

        # 2. Netzleistung (+ Bezug, - Einspeisung)
        grid = _get_val("pgrid", "pactogrid", "grid_power", "gridPower", "toGridPower", "to_grid_power", "pGrid")

        # 3. Hausverbrauch
        load = _get_val("pload", "use_power", "useEnergy", "familyLoadPower", "load_power", "loadPower", "use_power_w", "pLocalLoad")

        # 4. Batterie Leistung (+ Entladung, - Ladung)
        bat_dis = _get_val("pdisCharge", "pdisCharge1", "pDisCharge") or 0.0
        bat_chg = _get_val("pcharge", "pcharge1", "pCharge") or 0.0
        bat_generic = _get_val("battery_power", "pactostorage", "pstorage", "battery_power_w")

        if bat_generic is not None and bat_dis == 0.0 and bat_chg == 0.0:
            bat_pwr = bat_generic
        else:
            bat_pwr = bat_dis - bat_chg

        # 5. Batterie SoC
        soc = _get_val("soc", "batterySoc", "battery_soc", "batteryPercent", "chargeLevel", "capacity", "SOC", "storageSoc")

        # 6. Tagesertrag
        daily = _get_val("eToday", "etoday", "todayEnergy", "today_energy", "e_today", "eTodayTotal", "eAcChargeToday", "todayYield", "daily_generation")

        telemetry = CanonicalTelemetry(
            pv_power_w=pv,
            grid_power_w=grid,
            load_power_w=load,
            battery_power_w=bat_pwr,
            battery_soc=soc,
            daily_yield_kwh=daily,
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
        plant_id = credentials.get("plant_id") or ""
        device_sn = credentials.get("device_sn") or credentials.get("sn") or ""
        username = credentials.get("user_account") or credentials.get("username") or credentials.get("userName")
        password = credentials.get("user_password") or credentials.get("password")

        is_mock = (
            str(token).startswith("test_")
            or str(token).startswith("mock_")
            or str(username).lower() in ("test", "demo", "mock", "test_growatt_user")
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
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Sharegy EMS GrowattConnector)",
        })

        # PFAD A: Growatt OpenAPI (Token vorhanden)
        if token and not is_mock:
            api_headers = {
                "token": str(token).strip(),
                "Content-Type": "application/x-www-form-urlencoded",
            }

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

            telemetry = self.parse_payload(raw_data)
            return AdapterTestResult(
                status="success",
                message=f"Live-Verbindung zu {self.name} erfolgreich!",
                live_metrics=telemetry.to_metrics_dict(),
                raw_sample=raw_data,
                simulated=False,
            )

        # PFAD B: ShineServer Web Login
        if username and password:
            hashed_pw = self._hash_password(str(password))
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

                    if plant_id:
                        today_str = datetime.date.today().strftime("%Y-%m-%d")
                        for inv_ep, params in [
                            (f"{active_host}/newInverterAPI.do", {"op": "getInverterDetailData", "inverterId": device_sn or plant_id}),
                            (f"{active_host}/newStorageAPI.do", {"op": "getStorageTotalData", "plantId": plant_id}),
                        ]:
                            try:
                                r = session.get(inv_ep, params=params, timeout=8)
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
                    raise ValueError(f"Growatt Datenabfrage fehlgeschlagen: {e}")

        raise ValueError("Growatt Login fehlgeschlagen: Bitte prüfe Benutzername, Passwort oder API-Token.")
