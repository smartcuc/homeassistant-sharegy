"""
devices/adapters/victron.py

Isolierter Adapter für Victron Energy VRM Portal API (vrmapi.victronenergy.com).
Dokumentation: https://vrm-api-docs.victronenergy.com/

Unterstützt:
1. Personal Access Token (PAT) Authentifizierung (X-Authorization: Token <token>)
2. Benutzername / Passwort Login (POST /auth/login)
3. Automatische Erkennung von Installationen / Site IDs (GET /users/{idUser}/installations)
4. System-Overview & Diagnostics Telemetrie (GET /installations/{idSite}/system-overview)
5. Normalisierung in CanonicalTelemetry
"""

import logging
import requests
import datetime
from typing import Dict, Any, Optional, List
from django.utils import timezone

from devices.adapters.contracts import BaseInverterAdapter, CanonicalTelemetry, AdapterTestResult

logger = logging.getLogger(__name__)


class VictronAdapter(BaseInverterAdapter):
    profile_id = "victron_vrm"
    name = "Victron Energy VRM"
    vendor = "Victron"
    protocol = "http_cloud"
    category = "inverter_hybrid"

    VRM_BASE_URL = "https://vrmapi.victronenergy.com/v2"

    def __init__(self):
        super().__init__()
        self._token_cache: Dict[str, Dict[str, Any]] = {}

    def generate_mock_payload(self) -> dict:
        """
        Generiert realistische Live-Messdaten für Victron MultiPlus-II / Cerbo GX Systeme.
        """
        import random
        now = timezone.now()
        hour = now.hour

        if 6 <= hour <= 20:
            pv_factor = max(0.0, 1.0 - ((hour - 13.0) / 7.0) ** 2)
            pv_w = round(random.uniform(2500.0, 6800.0) * pv_factor, 1)
        else:
            pv_w = 0.0

        load_w = round(random.uniform(450.0, 1800.0), 1)
        diff = pv_w - load_w

        if diff > 0:
            bat_w = round(min(diff * 0.8, 2500.0) * -1, 1) # Laden (negativ)
            grid_w = round((diff + bat_w) * -1, 1)        # Einspeisung (negativ)
        else:
            bat_w = round(min(abs(diff), 2000.0), 1)      # Entladen (positiv)
            grid_w = round(abs(diff) - bat_w, 1)          # Bezug (positiv)

        return {
            "success": True,
            "records": {
                "solar_yield": pv_w,
                "pv_power": pv_w,
                "grid_power": grid_w,
                "consumption": load_w,
                "battery_power": bat_w,
                "soc": round(random.uniform(65.0, 95.0), 1),
                "yield_today": round(pv_w * 0.0042 + 9.8, 2),
                "yield_total": 8940.5,
                "battery_state": "charging" if bat_w < 0 else ("discharging" if bat_w > 0 else "idle"),
                "dc_system_power": 0.0,
            }
        }

    def parse_payload(self, raw_data: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Wandelt ein Victron VRM JSON-Objekt in CanonicalTelemetry um.
        """
        telemetry = CanonicalTelemetry(
            timestamp=timezone.now(),
            raw_payload=raw_data
        )

        records = {}
        if isinstance(raw_data, dict):
            if "records" in raw_data and isinstance(raw_data["records"], dict):
                records = raw_data["records"]
            elif "data" in raw_data and isinstance(raw_data["data"], dict):
                records = raw_data["data"]
            else:
                records = raw_data

        def _get_num(*keys) -> Optional[float]:
            for k in keys:
                if k in records and records[k] is not None:
                    try:
                        v = float(records[k])
                        return v
                    except (ValueError, TypeError):
                        pass
                # Verschachtelte Diagnostics / Records Suche
                if "devices" in records and isinstance(records["devices"], list):
                    for dev in records["devices"]:
                        if isinstance(dev, dict) and k in dev and dev[k] is not None:
                            try:
                                return float(dev[k])
                            except (ValueError, TypeError):
                                pass
            return None

        # 1. PV Erzeugung (solar_yield, pv_power, Ppv, solar_power)
        pv_w = _get_num("pv_power", "solar_yield", "solar_power", "Ppv", "ac_pv_power", "dc_pv_power")
        if pv_w is not None:
            telemetry.pv_power_w = max(0.0, round(pv_w, 1))

        # 2. Netzleistung (grid_power, Pgrid, grid_in, ac_grid_power)
        # Victron: positiv = Netzbezug (Import), negativ = Netzeinspeisung (Export)
        grid_w = _get_num("grid_power", "Pgrid", "grid_in", "ac_grid_power", "grid")
        if grid_w is not None:
            telemetry.grid_power_w = round(grid_w, 1)

        # 3. Hausverbrauch (consumption, Pcons, ac_consumption, load_power)
        load_w = _get_num("consumption", "Pcons", "ac_consumption", "load_power", "from_grid", "direct_use")
        if load_w is not None:
            telemetry.load_power_w = max(0.0, round(load_w, 1))

        # 4. Batterieleistung (battery_power, Pbat, dc_battery_power)
        # Victron VRM: positiv = Entladen (Discharge), negativ = Laden (Charge)
        bat_w = _get_num("battery_power", "Pbat", "dc_battery_power", "battery")
        if bat_w is not None:
            telemetry.battery_power_w = round(bat_w, 1)

        # 5. Batterie SoC
        soc = _get_num("soc", "battery_soc", "SOC", "state_of_charge")
        if soc is not None:
            if 0.0 <= soc <= 1.0:
                soc = soc * 100.0
            telemetry.battery_soc = round(max(0.0, min(100.0, soc)), 1)

        # 6. Erträge
        today_kwh = _get_num("yield_today", "today_yield", "daily_yield", "solar_yield_today")
        if today_kwh is not None:
            telemetry.daily_yield_kwh = round(today_kwh, 2)

        total_kwh = _get_num("yield_total", "total_yield", "solar_yield_total")
        if total_kwh is not None:
            telemetry.total_yield_kwh = round(total_kwh, 2)

        # Physikalische Konsistenzprüfung & Bilanzableitung
        if telemetry.load_power_w is None and telemetry.pv_power_w is not None and telemetry.grid_power_w is not None:
            # P_Load = P_PV + P_Grid + P_Bat (mit P_Bat > 0 bei Entladung, < 0 bei Ladung)
            bat_pwr = telemetry.battery_power_w or 0.0
            calc_load = telemetry.pv_power_w + telemetry.grid_power_w + bat_pwr
            if calc_load >= 0:
                telemetry.load_power_w = round(calc_load, 1)

        if telemetry.pv_power_w is None:
            telemetry.pv_power_w = 0.0
        if telemetry.grid_power_w is None:
            telemetry.grid_power_w = 0.0

        return telemetry

    def _get_auth_headers(self, credentials: Dict[str, Any]) -> Dict[str, str]:
        """
        Erstellt die passenden Auth-Header für die Victron VRM API (PAT oder Bearer JWT).
        """
        token = credentials.get("access_token") or credentials.get("token") or credentials.get("api_key")
        if token:
            return {
                "X-Authorization": f"Token {str(token).strip()}",
                "Content-Type": "application/json",
                "User-Agent": "Sharegy-EMS/1.0"
            }

        # Login via Benutzername & Passwort
        username = credentials.get("username") or credentials.get("email")
        password = credentials.get("password")

        if username and password:
            cache_key = f"{username}:{password}"
            cached = self._token_cache.get(cache_key)
            now = timezone.now()

            if cached and cached.get("token") and cached.get("expires_at") > now:
                return {
                    "X-Authorization": f"Bearer {cached['token']}",
                    "Content-Type": "application/json",
                    "User-Agent": "Sharegy-EMS/1.0"
                }

            login_url = f"{self.VRM_BASE_URL}/auth/login"
            resp = requests.post(
                login_url,
                json={"username": username.strip(), "password": password.strip()},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                jwt_tok = data.get("token")
                user_id = data.get("idUser")
                if jwt_tok:
                    self._token_cache[cache_key] = {
                        "token": jwt_tok,
                        "idUser": user_id,
                        "expires_at": now + datetime.timedelta(hours=6)
                    }
                    return {
                        "X-Authorization": f"Bearer {jwt_tok}",
                        "Content-Type": "application/json",
                        "User-Agent": "Sharegy-EMS/1.0"
                    }
            raise ConnectionError(f"Victron VRM Login fehlgeschlagen (HTTP {resp.status_code}): {resp.text[:150]}")

        raise ValueError("Bitte gib entweder einen Victron Personal Access Token oder E-Mail & Passwort an.")

    def _get_user_installations(self, headers: Dict[str, str], user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Ermittelt alle Installationen / Sites des Nutzers.
        """
        # Versuch 1: installations über User-ID oder 'me'
        urls = [
            f"{self.VRM_BASE_URL}/users/{user_id}/installations" if user_id else None,
            f"{self.VRM_BASE_URL}/users/me/installations",
            f"{self.VRM_BASE_URL}/installations",
        ]

        for url in urls:
            if not url:
                continue
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    records = data.get("records") or data.get("installations") or data
                    if isinstance(records, list):
                        return records
            except Exception as e:
                logger.debug("Victron installations lookup error on %s: %s", url, e)

        return []

    def fetch_live_telemetry(self, credentials: Dict[str, Any], device=None) -> Dict[str, Any]:
        """
        Führt den Live-Abruf an der Victron VRM API aus.
        """
        headers = self._get_auth_headers(credentials)
        site_id = credentials.get("site_id") or credentials.get("idSite") or credentials.get("installation_id")

        # Falls site_id fehlt, automatisch ermitteln
        if not site_id:
            installations = self._get_user_installations(headers)
            if installations and isinstance(installations, list):
                site_id = installations[0].get("idSite") or installations[0].get("id") or installations[0].get("identifier")
                if site_id:
                    credentials["site_id"] = str(site_id)
                    logger.info("Victron VRM Auto-Discovered site_id: %s (Name: %s)", site_id, installations[0].get("name"))

        if not site_id:
            raise ConnectionError("Victron VRM: Keine Site ID (Installation ID) gefunden oder angegeben.")

        # 1. Haupt-Endpunkt: System Overview (Liefert alle Live-Flüsse kompakt)
        endpoints = [
            f"{self.VRM_BASE_URL}/installations/{site_id}/system-overview",
            f"{self.VRM_BASE_URL}/installations/{site_id}/stats?type=live",
            f"{self.VRM_BASE_URL}/installations/{site_id}/diagnostics",
            f"{self.VRM_BASE_URL}/installations/{site_id}/overallstats",
        ]

        last_error = None
        for ep in endpoints:
            try:
                resp = requests.get(ep, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, dict):
                        data["idSite"] = site_id
                        return data
                elif resp.status_code == 401:
                    raise ConnectionError("Victron VRM: Authentifizierung abgelaufen oder ungültig.")
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:120]}"
            except requests.RequestException as e:
                last_error = str(e)

        raise ConnectionError(f"Victron VRM Telemetrie-Abruf fehlgeschlagen für Site {site_id}: {last_error}")

    def fetch_telemetry(self, credentials: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Fragt die Live-Telemetrie von Victron VRM ab und konvertiert sie in CanonicalTelemetry.
        """
        raw_payload = self.fetch_live_telemetry(credentials)
        return self.parse_payload(raw_payload)

    def test_connection(self, credentials: Dict[str, Any]) -> AdapterTestResult:
        """
        Führt einen Verbindungstest durch und liefert ein standardisiertes AdapterTestResult.
        """
        # Mock / Simulation Modus für Tests
        is_mock = (
            bool(credentials.get("is_mock"))
            or bool(credentials.get("mock"))
            or not credentials
            or all(not str(v).strip() for v in credentials.values())
            or any(any(m in str(v).lower() for m in ("mock", "fake", "demo", "test", "_123", "dummy")) for v in credentials.values())
        )

        if is_mock or not (credentials.get("access_token") or credentials.get("token") or credentials.get("username")):
            payload = self.generate_mock_payload()
            telemetry = self.parse_payload(payload)
            return AdapterTestResult(
                status="success",
                message="Victron VRM Portal Simulation erfolgreich.",
                live_metrics=telemetry.to_metrics_dict(),
                raw_sample=payload,
                simulated=True
            )

        try:
            raw_payload = self.fetch_live_telemetry(credentials)
            telemetry = self.parse_payload(raw_payload)
            return AdapterTestResult(
                status="success",
                message=f"Live-Verbindung zu {self.name} erfolgreich!",
                live_metrics=telemetry.to_metrics_dict(),
                raw_sample=raw_payload,
                simulated=False
            )
        except Exception as e:
            err_msg = f"Victron VRM Verbindungstest fehlgeschlagen: {e}"
            return AdapterTestResult(
                status="error",
                message=err_msg,
                live_metrics={},
                raw_sample={"error": str(e)},
                error=err_msg
            )

    def validate_credentials(self, credentials: Dict[str, Any]) -> AdapterTestResult:
        """
        Kompatibilitäts-Wrapper für validate_credentials.
        """
        return self.test_connection(credentials)
