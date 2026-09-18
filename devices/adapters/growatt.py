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
        # Realistische PV-Leistung für Simulation/Sandbox
        pv_w = round(random.uniform(3500.0, 7800.0), 1)

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
        Growatt liefert Leistungen in Watt oder kW und Energien in kWh.
        Unterstützt:
        - Vollständige Multimap-Traversierung aller verschachtelten Listen & Dictionaries
        - Multi-String-Ertragsberechnung (ppv1..ppv16, p_pv1..p_pv16, mppt1..mppt8)
        - 3-Phasen-Summierung (pac1 + pac2 + pac3)
        - Balkonkraftwerk & Noah 2000 Speicher (solarPower, outputPower)
        - DC Volt * Ampere Ertragsberechnung (vpv * ipv)
        - Automatische kW -> W Erkennung für Dezimalwerte (z. B. 2.45 kW -> 2450 W)
        - Physikalische Ertrags-Rekonstruktion aus Batterieladung + Netzeinspeisung + Eigenverbrauch
        """
        from collections import defaultdict
        flat_all: Dict[str, list] = defaultdict(list)
        flat: Dict[str, Any] = {}
        flat_latest: Dict[str, Any] = {}
        flat_units: Dict[str, str] = {}

        def _track_unit(orig_k: str, clean_k: str, clean_no_unit: str):
            k_low = str(orig_k).lower()
            if "_kwh" in k_low or "(kwh)" in k_low:
                unit = "kwh"
            elif "_wh" in k_low or "(wh)" in k_low:
                unit = "wh"
            elif "_kw" in k_low or "(kw)" in k_low:
                unit = "kw"
            elif "_w" in k_low or "(w)" in k_low:
                unit = "w"
            else:
                unit = None
            if unit:
                flat_units[orig_k] = unit
                flat_units[clean_k] = unit
                flat_units[clean_no_unit] = unit

        # 1. Neuesten Zeitreihen-Eintrag finden (z. B. aus 'datas', 'tlx', 'min', 'max' Arrays)
        latest_record = None
        if isinstance(raw_data, dict):
            responses = raw_data.get("responses", [])
            for r_item in reversed(responses):
                if isinstance(r_item, dict):
                    d_obj = r_item.get("data") if isinstance(r_item.get("data"), dict) else r_item
                    for candidate_key in ["datas", "tlx", "min", "max", "inv", "storage", "mix", "sph", "spa", "noah", "devices"]:
                        item_list = d_obj.get(candidate_key)
                        if isinstance(item_list, list) and item_list:
                            latest_record = item_list[-1]
                            break
                    if latest_record:
                        break

            if not latest_record:
                d_obj = raw_data.get("data") if isinstance(raw_data.get("data"), dict) else raw_data
                for candidate_key in ["datas", "tlx", "min", "max", "inv", "storage", "mix", "sph", "spa", "noah", "devices"]:
                    item_list = d_obj.get(candidate_key)
                    if isinstance(item_list, list) and item_list:
                        latest_record = item_list[-1]
                        break

        def _populate_dict(d: dict, target_dict: dict):
            for k, v in d.items():
                if isinstance(v, (int, float, str, bool)) or v is None:
                    clean_k = str(k).lower().replace(" ", "_").replace("(", "_").replace(")", "").replace("：", "").replace(":", "").replace("-", "_").strip()
                    clean_k2 = str(k).lower().replace(" ", "").replace("(", "").replace(")", "").replace("_", "").replace("：", "").replace(":", "").replace("-", "").strip()
                    clean_no_unit = clean_k.replace("_kw", "").replace("_kwh", "").replace("_w", "").replace("_wh", "")
                    target_dict[k] = v
                    target_dict[clean_k] = v
                    target_dict[clean_k2] = v
                    target_dict[clean_no_unit] = v
                    _track_unit(k, clean_k, clean_no_unit)

        if isinstance(latest_record, dict):
            _populate_dict(latest_record, flat_latest)

        def _walk(item):
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, (int, float, str, bool)) or v is None:
                        clean_k = str(k).lower().replace(" ", "_").replace("(", "_").replace(")", "").replace("：", "").replace(":", "").replace("-", "_").strip()
                        clean_k2 = str(k).lower().replace(" ", "").replace("(", "").replace(")", "").replace("_", "").replace("：", "").replace(":", "").replace("-", "").strip()
                        clean_no_unit = clean_k.replace("_kw", "").replace("_kwh", "").replace("_w", "").replace("_wh", "")

                        if v is not None:
                            flat_all[k].append(v)
                            flat_all[clean_k].append(v)
                            flat_all[clean_k2].append(v)
                            flat_all[clean_no_unit].append(v)
                            _track_unit(k, clean_k, clean_no_unit)

                        is_empty = v in (None, "", "-", "--", "null", "none", "n/a", "nan", "undefined")
                        if k not in flat or (flat[k] in (None, "", "-", "--", "null", "none", "n/a", "nan", "undefined") and not is_empty):
                            flat[k] = v
                        if clean_k not in flat or (flat[clean_k] in (None, "", "-", "--", "null", "none") and not is_empty):
                            flat[clean_k] = v
                        if clean_k2 not in flat or (flat[clean_k2] in (None, "", "-", "--", "null", "none") and not is_empty):
                            flat[clean_k2] = v
                        if clean_no_unit not in flat or (flat[clean_no_unit] in (None, "", "-", "--", "null", "none") and not is_empty):
                            flat[clean_no_unit] = v
                    elif isinstance(v, (dict, list)):
                        _walk(v)
            elif isinstance(item, list):
                for elem in item:
                    _walk(elem)

        _walk(raw_data)

        # Prüfen ob der Payload bereits Werte im Watt-Bereich (> 100 W) enthält
        has_large_watts = False
        for k_item, vals in flat_all.items():
            if any(pk in str(k_item).lower() for pk in ["pac", "ppv", "pload", "pcharge", "pdischarge", "pactogrid", "pfromgrid", "solarpower", "outputpower"]):
                for v_item in vals:
                    try:
                        import re as _re
                        _m = _re.search(r"[-+]?\d*\.?\d+", str(v_item).replace(",", "."))
                        if _m and abs(float(_m.group(0))) >= 100.0:
                            has_large_watts = True
                            break
                    except Exception:
                        pass
                if has_large_watts:
                    break

        def _get_val(*keys, is_power: bool = False, prefer_latest: bool = True) -> Optional[float]:
            # Zuerst aus flat_latest prüfen falls vorhanden
            if prefer_latest and flat_latest:
                for k in keys:
                    clean_k = str(k).lower().replace(" ", "_").replace("(", "_").replace(")", "").replace("：", "").replace(":", "").replace("-", "_").strip()
                    clean_k2 = str(k).lower().replace(" ", "").replace("(", "").replace(")", "").replace("_", "").replace("：", "").replace(":", "").replace("-", "").strip()
                    for cand_k in [k, clean_k, clean_k2]:
                        if cand_k in flat_latest and flat_latest[cand_k] is not None:
                            raw = str(flat_latest[cand_k]).strip().replace(",", ".")
                            if raw.lower() not in ("-", "--", "null", "none", "n/a", ""):
                                factor = 1.0
                                low = raw.lower()
                                k_low = str(k).lower()
                                cand_low = str(cand_k).lower()
                                has_kwh = "kwh" in low or "_kwh" in k_low or "(kwh)" in k_low or flat_units.get(k) == "kwh" or flat_units.get(cand_k) == "kwh"
                                has_wh = (("wh" in low and not has_kwh) or ("_wh" in k_low and not has_kwh) or flat_units.get(k) == "wh" or flat_units.get(cand_k) == "wh")
                                has_kw = (("kw" in low and not has_kwh) or ("(kw)" in k_low and not has_kwh) or ("_kw" in k_low and not has_kwh) or flat_units.get(k) == "kw" or flat_units.get(cand_k) == "kw")
                                has_w = (("w" in low and not has_kw and not has_kwh and not has_wh) or ("_w" in k_low and not has_kw and not has_kwh and not has_wh) or flat_units.get(k) == "w" or flat_units.get(cand_k) == "w")

                                if is_power:
                                    if has_kwh or has_wh:
                                        continue  # Energiewert (kWh/Wh) nicht als Leistung (W) werten
                                    if any(ek in k_low for ek in ["currentenergy", "current_energy", "currenergy", "curr_energy"]) and not has_kw:
                                        continue  # currentEnergy ohne explizite 'kW'-Einheit ist Energie
                                    if has_kw:
                                        factor = 1000.0
                                    elif has_w:
                                        factor = 1.0
                                else:
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
                                        if is_power and not has_w and not has_kw:
                                            # Nur reine Anlagen-Überblicksfelder (die laut Growatt-API per Definition in kW gemeldet werden) skalieren
                                            is_plant_kw_field = any(pk in k_low for pk in ["currentpower", "current_power", "plantpower", "plant_power", "currpower", "curr_power", "current_power_kw", "currentpowerkw", "plant_power_kw", "plantpowerkw"])
                                            if is_plant_kw_field or (val > 0 and val < 50.0 and not has_large_watts):
                                                val = val * 1000.0
                                        return val
                                    except (ValueError, TypeError):
                                        pass

            for k in keys:
                raw_list = flat_all.get(k, [])
                if k in flat and flat[k] not in raw_list:
                    raw_list = list(raw_list) + [flat[k]]

                for raw_item in reversed(raw_list):
                    if raw_item is None:
                        continue
                    raw = str(raw_item).strip().replace(",", ".")
                    if raw.lower() in ("-", "--", "null", "none", "n/a", ""):
                        continue
                    factor = 1.0
                    low = raw.lower()
                    k_low = str(k).lower()
                    has_kwh = "kwh" in low or "_kwh" in k_low or "(kwh)" in k_low or flat_units.get(k) == "kwh"
                    has_wh = (("wh" in low and not has_kwh) or ("_wh" in k_low and not has_kwh) or flat_units.get(k) == "wh")
                    has_kw = (("kw" in low and not has_kwh) or ("(kw)" in k_low and not has_kwh) or ("_kw" in k_low and not has_kwh) or flat_units.get(k) == "kw")
                    has_w = (("w" in low and not has_kw and not has_kwh and not has_wh) or ("_w" in k_low and not has_kw and not has_kwh and not has_wh) or flat_units.get(k) == "w")

                    if is_power:
                        if has_kwh or has_wh:
                            continue  # Energiewert (kWh/Wh) nicht als Leistung (W) werten
                        if any(ek in k_low for ek in ["currentenergy", "current_energy", "currenergy", "curr_energy"]) and not has_kw:
                            continue  # currentEnergy ohne explizite 'kW'-Einheit ist Energie
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
                            if is_power and not has_w and not has_kw:
                                # Nur reine Anlagen-Überblicksfelder (die laut Growatt-API per Definition in kW gemeldet werden) skalieren
                                is_plant_kw_field = any(pk in k_low for pk in ["currentpower", "current_power", "plantpower", "plant_power", "currpower", "curr_power", "current_power_kw", "currentpowerkw", "plant_power_kw", "plantpowerkw"])
                                if is_plant_kw_field or (val > 0 and val < 50.0 and not has_large_watts):
                                    val = val * 1000.0
                            return val  # Sobald der prioritäre Key gefunden wurde, sofort zurückliefern!
                        except (ValueError, TypeError):
                            pass
            return None

        # 2. Batterie Leistung (+ Entladung, - Ladung) & SoC zuerst einlesen für Plausibilisierung
        bat_dis = _get_val("pdisCharge", "pdisCharge1", "pDisCharge", "pDischarge", "discharge_power", "dischargePower", "disChargePowerOfBattery", is_power=True) or 0.0
        bat_chg = _get_val("pcharge", "pcharge1", "pCharge", "charge_power", "chargePower", "chargePowerOfBattery", is_power=True) or 0.0
        bat_to_storage = _get_val("pactostorage", "pstorage", "p_storage", "storage_power", is_power=True) or 0.0
        bat_generic = _get_val("battery_power", "battery_power_w", "batteryPower", "batPower", "B_P1", "bms_power", is_power=True)

        if bat_generic is not None and bat_dis == 0.0 and bat_chg == 0.0 and bat_to_storage == 0.0:
            bat_pwr = bat_generic
        elif bat_to_storage > 0 and bat_chg == 0:
            bat_pwr = -abs(bat_to_storage)
        else:
            bat_pwr = bat_dis - (bat_chg or bat_to_storage)

        # Batterie Volt * Ampere falls keine Watt geliefert wurden
        if abs(bat_pwr or 0.0) < 1.0:
            v_bat = _get_val("vbat", "v_bat", "vBat", "batteryVoltage", "battery_voltage", "bmsVbat", "bdc1Vbat") or 0.0
            i_bat = _get_val("ibat", "i_bat", "iBat", "batteryCurrent", "battery_current", "bmsIbat", "bdc1Ibat") or 0.0
            if v_bat > 0 and abs(i_bat) > 0.1:
                bat_pwr = round(v_bat * i_bat, 1)

        soc = _get_val("soc", "batterySoc", "battery_soc", "batteryPercent", "chargeLevel", "capacity", "SOC", "storageSoc", "bmsSoc", "bdc1Soc", "battery_level")

        # 1. PV Erzeugung: Reine DC-Solar-Eingangsleistung (von den Strings/Modulen)
        ppv_dc = _get_val(
            "solar_power", "solarpower", "solarPower",
            "ppv", "ppvTotal", "ppv_total", "p_pv", "pv_power", "pvPower", "pvpower", "pv_power_w", "pvPowerW", "pPv",
            "powerOfPhotovoltaic",
            is_power=True
        )

        # Multi-String PV Summe (String 1 bis String 16)
        string_powers = []
        for s_idx in range(1, 17):
            s_val = _get_val(f"ppv{s_idx}", f"pPv{s_idx}", f"p_pv{s_idx}", f"pv{s_idx}_power", f"mppt{s_idx}_power", f"mppt{s_idx}", is_power=True)
            if s_val and s_val > 0:
                string_powers.append(s_val)
        ppv_string_sum = sum(string_powers) if string_powers else 0.0

        # Volt * Ampere Strings (falls nur Spannungen und Ströme geliefert werden)
        va_sum = 0.0
        for s_idx in range(1, 9):
            v_s = _get_val(f"vpv{s_idx}", f"vPv{s_idx}", f"v_pv{s_idx}") or 0.0
            i_s = _get_val(f"ipv{s_idx}", f"iPv{s_idx}", f"i_pv{s_idx}") or 0.0
            if v_s > 0 and i_s > 0:
                va_sum += (v_s * i_s)
        va_string_sum = round(va_sum, 1) if va_sum > 0 else 0.0

        # AC Wechselrichter-Ausgangsleistung (kann bei Hybrid-Invertern auch Batterie-Entladung enthalten)
        pac_ac = _get_val(
            "pac", "invPac", "inv_pac",
            "pAct", "pact", "p_act",
            "output_power", "outputpower", "outputPower", "outPutPower",
            "active_power", "activePower", "real_power", "realPower",
            "inverter_power", "inverterPower", "ac_power", "acPower",
            "sys_power", "syspower",
            is_power=True
        )
        curr_power = _get_val(
            "currentPower", "current_power", "currPower", "curr_power", "plantPower",
            "plant_power", "current_power_kw", "currentpowerkw", "currentEnergy", "current_energy",
            is_power=True
        )

        # 3-Phasen AC Summe (pac1 + pac2 + pac3)
        pac1 = _get_val("pac1", "invPac1", "inv_pac1", "power1", is_power=True) or 0.0
        pac2 = _get_val("pac2", "invPac2", "inv_pac2", "power2", is_power=True) or 0.0
        pac3 = _get_val("pac3", "invPac3", "inv_pac3", "power3", is_power=True) or 0.0
        pac_3phase_sum = (pac1 + pac2 + pac3) if (pac1 + pac2 + pac3) > 0 else 0.0

        # Prioritätsauswahl für PV Erzeugung:
        # Priorität 1: Reines DC Solarfeld (z. B. ppv oder Stringsumme)
        if ppv_dc is not None:
            pv = ppv_dc
        elif ppv_string_sum > 0:
            pv = ppv_string_sum
        elif va_string_sum > 0:
            pv = va_string_sum
        # Priorität 2: AC-Ausgangsleistung (unter Abzug von Batterieentladung bei Dunkelheit)
        elif pac_ac is not None:
            # Bei Hybrid-Wechselrichtern: AC-Leistung minus Batterieentladeleistung = echte Solarleistung (0W bei Dunkelheit)
            bat_discharge_now = max(0.0, float(bat_pwr or 0.0))
            pv = max(0.0, pac_ac - bat_discharge_now)
        elif pac_3phase_sum > 0:
            bat_discharge_now = max(0.0, float(bat_pwr or 0.0))
            pv = max(0.0, pac_3phase_sum - bat_discharge_now)
        elif curr_power is not None:
            bat_discharge_now = max(0.0, float(bat_pwr or 0.0))
            pv = max(0.0, curr_power - bat_discharge_now)
        else:
            pv = 0.0
        if abs(bat_pwr or 0.0) < 1.0:
            v_bat = _get_val("vbat", "v_bat", "vBat", "batteryVoltage", "battery_voltage", "bmsVbat", "bdc1Vbat") or 0.0
            i_bat = _get_val("ibat", "i_bat", "iBat", "batteryCurrent", "battery_current", "bmsIbat", "bdc1Ibat") or 0.0
            if v_bat > 0 and abs(i_bat) > 0.1:
                bat_pwr = round(v_bat * i_bat, 1)

        soc = _get_val("soc", "batterySoc", "battery_soc", "batteryPercent", "chargeLevel", "capacity", "SOC", "storageSoc", "bmsSoc", "bdc1Soc", "battery_level")

        # 3. Netzleistung (+ Bezug, - Einspeisung)
        grid_export_val = _get_val("pactogrid", "toGridPower", "to_grid_power", "pToGrid", "feed_in_power", "p_feed_in", "feedInPower", "powerOfGridFeed", "pacToGridTotal", is_power=True)
        grid_import_val = _get_val("pfromgrid", "fromGridPower", "gridPurchasedPower", "pFromGrid", "p_import", "import_power", "gridImportPower", "powerOfGridTake", is_power=True)
        grid_net = _get_val("pgrid", "pGrid", "grid_power", "gridPower", "grid_power_w", is_power=True)

        if grid_export_val is not None or grid_import_val is not None:
            grid = float(grid_import_val or 0.0) - float(grid_export_val or 0.0)
        elif grid_net is not None:
            grid = float(grid_net)
        else:
            grid = None

        # 4. Hausverbrauch (pactouser / pLocalLoad / pload)
        load = _get_val("pactouser", "pLocalLoad", "pToUser", "pload", "p_load", "use_power", "useEnergy", "familyLoadPower", "load_power", "loadPower", "use_power_w", "home_load", "consumption", "powerOfLoad", "pacToLocalLoad", "pacToUserTotal", is_power=True)

        # 5. Physikalische Plausibilisierung für Grid, Battery, Load & PV-Rekonstruktion
        pv_val = max(0.0, float(pv or 0.0))
        bat_val = float(bat_pwr or 0.0)
        soc_val = float(soc) if soc is not None else None
        eff_load = float(load) if (load is not None and load > 0) else None

        # PV-Rekonstruktion aus Bilanz (falls Inverter 0W meldet, aber Batterie lädt oder ins Netz gespeist wird)
        bat_charging = abs(min(0.0, bat_val))
        bat_discharging = max(0.0, bat_val)
        grid_export = abs(min(0.0, float(grid or 0.0)))
        grid_import = max(0.0, float(grid or 0.0))
        eff_load_calc = eff_load or 0.0

        if pv_val <= 1.0:
            # PV-Rekonstruktion nur wenn physisch Erzeugung nachweisbar ist (Batterieladung oder Netzeinspeisung)
            if bat_charging > 30.0 or grid_export > 30.0:
                reconstructed_pv = eff_load_calc + bat_charging + grid_export - bat_discharging - grid_import
                if reconstructed_pv > 30.0:
                    pv_val = round(reconstructed_pv, 1)
                    pv = pv_val

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
            "epv1Today", "epv1today", "epvtoday", "epvToday", "eacToday", "eactoday",
            "esystemToday", "esystemtoday", "elocalLoadToday", "etoUserToday",
            "eToday", "etoday", "todayEnergy", "today_energy", "e_today", "eTodayTotal",
            "eAcChargeToday", "todayYield", "daily_generation", "solar_yield",
            "generationToday", "generation_today", "generation_today_kwh", "generationtodaykwh",
            "generationtoday"
        )
        total = _get_val(
            "epvTotal", "epvtotal", "epv1Total", "epv1total", "eacTotal", "eactotal",
            "esystemTotal", "esystemtotal", "etoUserTotal", "elocalLoadTotal",
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
            or username.lower() in ("test", "demo", "mock", "test_growatt_user", "mock_growatt_user")
            or username.lower().startswith("test_")
            or username.lower().startswith("mock_")
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

        raw_data: Dict[str, Any] = {"data": {}, "responses": []}
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Requested-With": "XMLHttpRequest",
        })

        def _merge_payload_item(resp_json):
            if not resp_json:
                return
            raw_data["responses"].append(resp_json)
            
            def _walk_merge(item):
                if isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, (int, float, str, bool)) or v is None:
                            is_empty = v in (None, "", "-", "--", "null", "none", "n/a", "nan", "undefined")
                            if not is_empty or k not in raw_data["data"]:
                                raw_data["data"][k] = v
                        elif isinstance(item, (dict, list)):
                            _walk_merge(v)
                elif isinstance(item, list):
                    for el in item:
                        _walk_merge(el)

            _walk_merge(resp_json)

        def _extract_all_sns(data) -> list:
            found = []
            sn_target_keys = {
                "sn", "devicesn", "device_sn", "inverterid", "inverter_id", "invsn", "inv_sn",
                "tlxsn", "tlx_sn", "minsn", "min_sn", "mixsn", "mix_sn", "sphsn", "sph_sn",
                "spasn", "spa_sn", "spfsn", "spf_sn", "maxsn", "max_sn", "midsn", "mid_sn",
                "micsn", "mic_sn", "hpssn", "hps_sn", "noahsn", "noah_sn", "storagesn", "storage_sn",
                "groboostsn", "groboost_sn", "datalogsn", "datalog_sn", "serialnum", "serial_num"
            }

            def _walk_sn(item):
                if isinstance(item, dict):
                    for k, v in item.items():
                        k_clean = str(k).lower().replace(" ", "").replace("_", "").replace("-", "")
                        if k_clean in sn_target_keys and v:
                            s = str(v).strip()
                            if len(s) >= 5 and s.lower() not in ("null", "none", "false", "true", "undefined", "default"):
                                if s not in found:
                                    found.append(s)
                        _walk_sn(v)
                elif isinstance(item, list):
                    for el in item:
                        _walk_sn(el)

            _walk_sn(data)
            return found

        # PFAD A: Growatt OpenAPI (Token / API-Key vorhanden)
        if token and not is_mock:
            from datetime import datetime
            from django.core.cache import cache
            token_clean = str(token).strip()
            api_headers = {
                "token": token_clean,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
            }
            today_str = datetime.now().strftime("%Y-%m-%d")
            cache_key = f"growatt:telemetry:{plant_id}:{device_sn or 'all'}"

            discovered_sn_list = [device_sn] if device_sn else []
            device_types: Dict[str, int] = {}
            api_call_succeeded = False
            last_openapi_err = None
            rate_limited = False
            base_host = "https://openapi.growatt.com"

            # 1. Falls device_sn noch nicht bekannt ist: Geräteliste abfragen
            if not device_sn and plant_id:
                try:
                    d_resp = session.get(f"{base_host}/v1/device/list", headers=api_headers, params={"token": token_clean, "plant_id": plant_id}, timeout=8)
                    if d_resp.status_code == 200:
                        d_json = d_resp.json()
                        if isinstance(d_json, dict) and d_json.get("error_code") == 0:
                            api_call_succeeded = True
                            _merge_payload_item(d_json)
                            devices = d_json.get("data", {}).get("devices", [])
                            for d in devices:
                                sn_item = str(d.get("device_sn") or "").strip()
                                if sn_item:
                                    if sn_item not in discovered_sn_list:
                                        discovered_sn_list.append(sn_item)
                                    device_types[sn_item] = d.get("type", 7)
                        elif d_json.get("error_code") == 10012:
                            rate_limited = True
                        elif d_json.get("error_msg"):
                            last_openapi_err = d_json.get("error_msg")
                except Exception as e:
                    logger.debug("Growatt device/list lookup failed: %s", e)

            # 2. Spezifische Inverter-Detail-Endpunkte für die Seriennummer abfragen
            if device_sn:
                target_sns = [device_sn]
            else:
                target_sns = discovered_sn_list if discovered_sn_list else []

            # Priorisierte Liste von Telemetrie-Endpunkten (TLX / Balkonkraftwerk zuerst)
            default_endpoints = [
                ("/v1/device/tlx/tlx_data", "tlx_sn"),
                ("/v1/device/min/min_data", "min_sn"),
                ("/v1/device/max/max_data", "max_sn"),
                ("/v1/device/storage/storage_data", "storage_sn"),
                ("/v1/device/sph/sph_data", "sph_sn"),
                ("/v1/device/mix/mix_data", "mix_sn"),
            ]
            type_to_endpoints = {
                7: [("/v1/device/tlx/tlx_data", "tlx_sn"), ("/v1/device/noah/noah_data", "noah_sn"), ("/v1/device/sph/sph_data", "sph_sn")],
                6: [("/v1/device/min/min_data", "min_sn"), ("/v1/device/tlx/tlx_data", "tlx_sn")],
                5: [("/v1/device/mid/mid_data", "mid_sn"), ("/v1/device/tlx/tlx_data", "tlx_sn")],
                4: [("/v1/device/max/max_data", "max_sn"), ("/v1/device/tlx/tlx_data", "tlx_sn")],
                2: [("/v1/device/storage/storage_data", "storage_sn"), ("/v1/device/spa/spa_data", "spa_sn"), ("/v1/device/mix/mix_data", "mix_sn")],
                1: [("/v1/device/inverter/inverter_data", "inverter_sn"), ("/v1/device/tlx/tlx_data", "tlx_sn")],
            }

            for sn_val in target_sns:
                dev_type = device_types.get(sn_val, 7)
                endpoints_to_try = type_to_endpoints.get(dev_type, default_endpoints)

                for ep_path, sn_key in endpoints_to_try:
                    try:
                        post_data = {
                            "token": token_clean,
                            sn_key: sn_val,
                            "device_sn": sn_val,
                            "start_date": today_str,
                            "end_date": today_str,
                            "page": 1,
                            "perpage": 50,
                        }
                        if plant_id:
                            post_data["plant_id"] = plant_id

                        inv_resp = session.post(f"{base_host}{ep_path}", headers=api_headers, data=post_data, timeout=8)
                        if inv_resp.status_code == 200:
                            inv_json = inv_resp.json()
                            if isinstance(inv_json, dict):
                                err_code = inv_json.get("error_code")
                                if err_code == 0:
                                    api_call_succeeded = True
                                    _merge_payload_item(inv_json)
                                    # Wenn wir Daten gefunden haben, direkt abbrechen um Rate-Limits zu schonen
                                    break
                                elif err_code == 10012:
                                    rate_limited = True
                                elif inv_json.get("error_msg"):
                                    last_openapi_err = inv_json.get("error_msg")
                    except Exception as e:
                        logger.debug("Growatt %s lookup failed: %s", ep_path, e)

            # 3. Anlagen-Übersicht als Fallback abfragen falls noch keine Telemetrie gefunden wurde
            if not api_call_succeeded and plant_id and not rate_limited:
                try:
                    p_resp = session.get(f"{base_host}/v1/plant/energy", headers=api_headers, params={"token": token_clean, "plant_id": plant_id, "date": today_str}, timeout=8)
                    if p_resp.status_code == 200:
                        p_json = p_resp.json()
                        if isinstance(p_json, dict) and p_json.get("error_code") == 0:
                            api_call_succeeded = True
                            _merge_payload_item(p_json)
                except Exception:
                    pass

            # 4. Cache-Handling: Bei Erfolg cachen (TTL: 5 Min.), bei Rate-Limit Cache nutzen
            if api_call_succeeded and (raw_data["data"] or raw_data["responses"]):
                try:
                    cache.set(cache_key, raw_data, timeout=300)
                except Exception:
                    pass
            elif rate_limited or (not api_call_succeeded and not raw_data["data"]):
                try:
                    cached_raw = cache.get(cache_key)
                    if cached_raw and isinstance(cached_raw, dict) and (cached_raw.get("data") or cached_raw.get("responses")):
                        logger.info("Growatt rate-limited (error_frequently_access). Using cached live telemetry snapshot.")
                        raw_data = cached_raw
                        api_call_succeeded = True
                        rate_limited = False
                except Exception as c_err:
                    logger.debug("Cache lookup failed: %s", c_err)

            if rate_limited and not raw_data["data"] and not raw_data["responses"]:
                err_msg = "Growatt OpenAPI Rate-Limit erreicht (error_frequently_access). Growatt beschränkt Abfragen auf 60s. Bitte kurz warten."
                return AdapterTestResult(status="error", error=err_msg, message=err_msg)

            if not api_call_succeeded and (last_openapi_err or (not raw_data["data"] and not raw_data["responses"])):
                if "permission" in str(last_openapi_err).lower():
                    err_msg = (
                        f"Growatt OpenAPI Fehler: '{last_openapi_err}'. "
                        "Dieser Growatt API-Token besitzt keine Leseberechtigung für die Cloud-Endpunkte "
                        "(oder ist im Growatt-Entwicklerportal noch nicht für Datenabfragen freigeschaltet)."
                    )
                else:
                    err_msg = f"Growatt OpenAPI Fehler: {last_openapi_err or 'Ungültiger API-Token oder Wechselrichter offline'}"
                return AdapterTestResult(status="error", error=err_msg, message=err_msg)

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
                        _merge_payload_item(p_j)
                        plants_info = p_j.get("back") if isinstance(p_j.get("back"), dict) else p_j
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
                                real_num_id = str(matched_plant.get("plantId") or matched_plant.get("id") or "")
                                if real_num_id:
                                    plant_id = real_num_id
                                    credentials["plant_id"] = plant_id
                                    logger.info("Growatt Web Login resolved plant_id: %s (Name: %s)", plant_id, matched_plant.get("plantName"))

                    # 2. Plant Detail API (Primary Plant Telemetry Endpoint)
                    if plant_id:
                        try:
                            p_det_resp = session.get(
                                f"{active_host}/PlantDetailAPI.do",
                                params={"plantId": plant_id, "type": "1", "date": today_str},
                                timeout=10,
                            )
                            if p_det_resp.status_code == 200:
                                _merge_payload_item(p_det_resp.json())
                        except Exception as p_det_err:
                            logger.debug("PlantDetailAPI query failed: %s", p_det_err)

                    # 3. Inverter Device Discovery für die Anlage (Rekursiv über alle Servlets)
                    discovered_devices = []
                    if device_sn:
                        discovered_devices.append(device_sn)

                    if plant_id:
                        device_discovery_endpoints = [
                            (
                                f"{active_host}/newTwoPlantAPI.do",
                                {"op": "getAllPlantListTwo", "plantId": plant_id, "userName": username},
                                {
                                    "language": "1",
                                    "nominalPower": "",
                                    "order": "1",
                                    "pageSize": "15",
                                    "plantName": "",
                                    "plantStatus": "",
                                    "toPageNum": "1",
                                    "plantId": plant_id,
                                    "userName": username,
                                },
                            ),
                            (f"{active_host}/newPlantAPI.do", {"op": "getPlantList"}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getPlantDevice", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getDeviceList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getInverterList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getStorageList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getMinList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getMixList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getTlxList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getSphList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getSpaList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getSpfList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getMaxList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getMidList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getMicList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/newPlantAPI.do", {"op": "getNoahList", "plantId": plant_id}, {"plantId": plant_id}),
                            (f"{active_host}/device/getDeviceList", None, {"plantId": plant_id}),
                            (f"{active_host}/device/getInverterList", None, {"plantId": plant_id}),
                            (f"{active_host}/device/getStorageList", None, {"plantId": plant_id}),
                            (f"{active_host}/panel/getPlantData", None, {"plantId": plant_id}),
                            (f"{active_host}/panel/getPlantData", {"plantId": plant_id}, None),
                            (f"{active_host}/newPlantAPI.do", {"op": "getPlantData", "plantId": plant_id}, None),
                            (f"{active_host}/indexLogAPI.do", {"op": "getPlantData"}, {"plantId": plant_id}),
                        ]

                        for plant_ep, params, post_data in device_discovery_endpoints:
                            try:
                                if post_data is not None:
                                    inv_list_resp = session.post(plant_ep, params=params, data=post_data, timeout=8)
                                else:
                                    inv_list_resp = session.get(plant_ep, params=params, timeout=8)
                                if inv_list_resp.status_code == 200:
                                    inv_data = inv_list_resp.json()
                                    _merge_payload_item(inv_data)
                                    # Rekursiv alle Seriennummern extrahieren
                                    for sn in _extract_all_sns(inv_data):
                                        if sn and sn not in discovered_devices:
                                            discovered_devices.append(sn)
                            except Exception:
                                pass

                    # Falls ein SN erkannt wurde, in credentials für schnelles Re-Polling sichern
                    if discovered_devices and not device_sn:
                        device_sn = discovered_devices[0]
                        credentials["device_sn"] = device_sn
                        logger.info("Growatt Web Login resolved inverter SNs: %s", discovered_devices)

                    # 4. Detaillierte Live-Abfragen für alle erkannten Wechselrichter & Speicher
                    target_sn_list = discovered_devices if discovered_devices else ([device_sn] if device_sn else [""])

                    for sn in target_sn_list:
                        common_payload = {
                            "plantId": plant_id,
                            "id": sn,
                            "inverterId": sn,
                            "deviceSn": sn,
                            "sn": sn,
                            "tlxSn": sn,
                            "minSn": sn,
                            "mixSn": sn,
                            "sphSn": sn,
                            "spaSn": sn,
                            "maxSn": sn,
                            "midSn": sn,
                            "micSn": sn,
                            "spfSn": sn,
                            "hpsSn": sn,
                            "noahSn": sn,
                            "storageSn": sn,
                            "groBoostSn": sn,
                            "date": today_str,
                            "type": "1",
                        }

                        for inv_ep, params in [
                            (f"{active_host}/newInverterAPI.do", {"op": "getInverterDetailData", "inverterId": sn, "id": sn}),
                            (f"{active_host}/newInverterAPI.do", {"op": "getInverterDetailData_two", "inverterId": sn, "id": sn}),
                            (f"{active_host}/newInverterAPI.do", {"op": "getInverterData", "id": sn, "type": "1", "date": today_str}),
                            (f"{active_host}/newInverterAPI.do", {"op": "getInverterTotalData", "inverterId": sn, "plantId": plant_id}),
                            (f"{active_host}/panel/getInverterData", {"inverterId": sn, "plantId": plant_id}),
                            (f"{active_host}/newTlxApi.do", {"op": "getEnergyOverview", "tlxSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newTlxApi.do", {"op": "getSystemStatus_KW", "tlxSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newTlxApi.do", {"op": "getTlxDetailData", "tlxSn": sn, "id": sn}),
                            (f"{active_host}/newMinApi.do", {"op": "getEnergyOverview", "minSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newMinApi.do", {"op": "getSystemStatus_KW", "minSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newMinApi.do", {"op": "getMinDetailData", "minSn": sn, "id": sn}),
                            (f"{active_host}/newMixApi.do", {"op": "getEnergyOverview", "mixSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newMixApi.do", {"op": "getSystemStatus_KW", "mixSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newMixApi.do", {"op": "getMixDetailData", "mixSn": sn, "id": sn}),
                            (f"{active_host}/newSphApi.do", {"op": "getEnergyOverview", "sphSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newSphApi.do", {"op": "getSystemStatus_KW", "sphSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newSphApi.do", {"op": "getSphDetailData", "sphSn": sn, "id": sn}),
                            (f"{active_host}/newSpaApi.do", {"op": "getEnergyOverview", "spaSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newSpaApi.do", {"op": "getSystemStatus_KW", "spaSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newSpaApi.do", {"op": "getSpaDetailData", "spaSn": sn, "id": sn}),
                            (f"{active_host}/newMaxApi.do", {"op": "getEnergyOverview", "maxSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newMaxApi.do", {"op": "getMaxDetailData", "maxSn": sn, "id": sn}),
                            (f"{active_host}/newMidApi.do", {"op": "getEnergyOverview", "midSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newMidApi.do", {"op": "getMidDetailData", "midSn": sn, "id": sn}),
                            (f"{active_host}/newMicApi.do", {"op": "getEnergyOverview", "micSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newMicApi.do", {"op": "getMicDetailData", "micSn": sn, "id": sn}),
                            (f"{active_host}/newSpfApi.do", {"op": "getEnergyOverview", "spfSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newSpfApi.do", {"op": "getSystemStatus_KW", "spfSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newSpfApi.do", {"op": "getSpfDetailData", "spfSn": sn, "id": sn}),
                            (f"{active_host}/newHpsApi.do", {"op": "getEnergyOverview", "hpsSn": sn, "id": sn, "plantId": plant_id}),
                            (f"{active_host}/newGroBoostApi.do", {"op": "getEnergyOverview", "groBoostSn": sn, "plantId": plant_id}),
                            (f"{active_host}/newNoahApi.do", {"op": "getNoahDetailData", "noahSn": sn}),
                            (f"{active_host}/newNoahApi.do", {"op": "getNoahEnergyOverview", "noahSn": sn}),
                        ]:
                            try:
                                merged_data = dict(common_payload)
                                if params:
                                    merged_data.update(params)
                                r = session.post(inv_ep, data=merged_data, timeout=8)
                                if r.status_code == 200:
                                    _merge_payload_item(r.json())
                                else:
                                    r_get = session.get(inv_ep, params=merged_data, timeout=8)
                                    if r_get.status_code == 200:
                                        _merge_payload_item(r_get.json())
                            except Exception:
                                pass

                    # 5. Speicher- & Gesamtstatus der Anlage
                    if plant_id:
                        for stor_ep, params, p_data in [
                            (f"{active_host}/newStorageAPI.do", {"op": "getStorageTotalData"}, {"plantId": plant_id}),
                            (f"{active_host}/newStorageAPI.do", {"op": "getStorageEnergyOverview"}, {"plantId": plant_id}),
                            (f"{active_host}/newStorageAPI.do", {"op": "getStorageDetailData"}, {"plantId": plant_id}),
                        ]:
                            try:
                                r = session.post(stor_ep, params=params, data=p_data, timeout=8)
                                if r.status_code == 200:
                                    _merge_payload_item(r.json())
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
                    if raw_data.get("data") or raw_data.get("responses"):
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

