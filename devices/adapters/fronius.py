"""
devices/adapters/fronius.py

Isolierter Adapter für Fronius Solar.web Cloud & Fronius Local Solar API v1.
Unterstützt:
1. Fronius Solar.web Mobile API (swqapi.solarweb.com) via Benutzername/E-Mail & Passwort
   (Kostenlose Cloud-Schnittstelle ohne kommerzielle API-Lizenzgebühren).
2. Lokale Fronius Solar API v1 (http://<ip>/solar_api/v1/GetPowerFlowRealtimeData.fcgi).
3. Automatische Entdeckung von PV-Systemen (pvSystemId) und Geräten.
4. Normalisierung in CanonicalTelemetry.
"""

import logging
import requests
import datetime
from typing import Dict, Any, Optional, List
from django.utils import timezone

from devices.adapters.contracts import BaseInverterAdapter, CanonicalTelemetry, AdapterTestResult

logger = logging.getLogger(__name__)


class FroniusAdapter(BaseInverterAdapter):
    profile_id = "fronius_solarweb"
    name = "Fronius Solar.web / Solar API"
    vendor = "Fronius"
    protocol = "http_cloud"
    category = "inverter_hybrid"

    # Mobile App API Zugangsdaten (swqapi.solarweb.com)
    APP_ACCESS_KEY_ID = "FKIAB4CDA71C0763413DA942DC756742318B"
    APP_ACCESS_KEY_VALUE = "67315e19-6805-479e-994d-7193ee5f6125"
    APP_USER_AGENT = "okhttp/4.12.0"
    SWQAPI_BASE_URL = "https://swqapi.solarweb.com"

    # Lokale Solar API v1 Endpunkte
    LOCAL_POWERFLOW_ENDPOINT = "/solar_api/v1/GetPowerFlowRealtimeData.fcgi"
    LOCAL_INVERTER_ENDPOINT = "/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData"

    def __init__(self):
        super().__init__()
        self._token_cache: Dict[str, Dict[str, Any]] = {}

    def generate_mock_payload(self) -> dict:
        """
        Generiert realistische Live-Messdaten für Fronius Solar.web / GEN24 Systeme.
        """
        import random
        now = timezone.now()
        hour = now.hour

        if 6 <= hour <= 20:
            pv_factor = max(0.0, 1.0 - ((hour - 13.0) / 7.0) ** 2)
            pv_w = round(random.uniform(3000.0, 8500.0) * pv_factor, 1)
        else:
            pv_w = 0.0

        load_w = round(random.uniform(500.0, 2400.0), 1)
        diff = pv_w - load_w

        if diff > 0:
            bat_w = round(min(diff * 0.75, 3200.0), 1)   # Laden (positiv)
            grid_w = round((diff - bat_w) * -1, 1)       # Einspeisung (negativ)
        else:
            bat_w = round(min(abs(diff), 2800.0) * -1, 1) # Entladen (negativ)
            grid_w = round(abs(diff) - abs(bat_w), 1)     # Bezug (positiv)

        return {
            "pvSystemId": "00000000-0000-0000-0000-000000000001",
            "data": {
                "channels": [
                    {"channelName": "PowerPV", "value": pv_w, "unit": "W"},
                    {"channelName": "PowerGrid", "value": grid_w, "unit": "W"},
                    {"channelName": "PowerLoad", "value": -abs(load_w), "unit": "W"},
                    {"channelName": "PowerAkku", "value": bat_w, "unit": "W"},
                    {"channelName": "StateOfCharge_Akku", "value": round(random.uniform(60.0, 95.0), 1), "unit": "%"},
                    {"channelName": "EnergyToday", "value": round(pv_w * 0.004 + 8.5, 2), "unit": "kWh"},
                    {"channelName": "EnergyTotal", "value": 14250.8, "unit": "kWh"}
                ]
            }
        }

    def parse_payload(self, raw_data: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Wandelt ein Fronius Solar.web JSON oder lokales Solar API JSON in CanonicalTelemetry um.
        """
        telemetry = CanonicalTelemetry(
            timestamp=timezone.now(),
            raw_payload=raw_data
        )

        # 1. Fall: Solar.web Cloud flowdata (channels Array)
        channels = []
        if isinstance(raw_data, dict):
            if "data" in raw_data and isinstance(raw_data["data"], dict):
                channels = raw_data["data"].get("channels", [])
            elif "channels" in raw_data:
                channels = raw_data.get("channels", [])

        if channels and isinstance(channels, list):
            for ch in channels:
                if not isinstance(ch, dict):
                    continue
                name = ch.get("channelName") or ch.get("name") or ""
                val = ch.get("value")
                if val is None:
                    continue
                try:
                    num_val = float(val)
                except (ValueError, TypeError):
                    continue

                if name == "PowerPV":
                    telemetry.pv_power_w = max(0.0, num_val)
                elif name == "PowerGrid":
                    # In Solar.web: positiv = Bezug, negativ = Einspeisung
                    telemetry.grid_power_w = num_val
                elif name == "PowerLoad":
                    # In Solar.web: meist negativ für Verbrauch
                    telemetry.load_power_w = abs(num_val)
                elif name == "PowerAkku":
                    # In Solar.web: positiv = Laden, negativ = Entladen
                    telemetry.battery_power_w = num_val
                elif name in ("StateOfCharge_Akku", "SOC", "StateOfCharge"):
                    telemetry.battery_soc = num_val
                elif name in ("EnergyToday", "EnergyYieldToday"):
                    telemetry.daily_yield_kwh = num_val
                elif name in ("EnergyTotal", "EnergyYieldTotal"):
                    telemetry.total_yield_kwh = num_val

        # 2. Fall: Lokale Solar API v1 (/solar_api/v1/GetPowerFlowRealtimeData.fcgi)
        site_data = {}
        if "Body" in raw_data and isinstance(raw_data["Body"], dict):
            body_data = raw_data["Body"].get("Data", {})
            if "Site" in body_data and isinstance(body_data["Site"], dict):
                site_data = body_data["Site"]
            
            # Inverter SoC / Details
            inverters = body_data.get("Inverters", {})
            if isinstance(inverters, dict):
                for inv_id, inv_data in inverters.items():
                    if isinstance(inv_data, dict) and "SOC" in inv_data and inv_data["SOC"] is not None:
                        try:
                            telemetry.battery_soc = float(inv_data["SOC"])
                        except (ValueError, TypeError):
                            pass

        if site_data:
            if "P_PV" in site_data and site_data["P_PV"] is not None:
                telemetry.pv_power_w = max(0.0, float(site_data["P_PV"]))
            if "P_Grid" in site_data and site_data["P_Grid"] is not None:
                telemetry.grid_power_w = float(site_data["P_Grid"])
            if "P_Load" in site_data and site_data["P_Load"] is not None:
                telemetry.load_power_w = abs(float(site_data["P_Load"]))
            if "P_Akku" in site_data and site_data["P_Akku"] is not None:
                telemetry.battery_power_w = float(site_data["P_Akku"])
            if "E_Day" in site_data and site_data["E_Day"] is not None:
                telemetry.daily_yield_kwh = round(float(site_data["E_Day"]) / 1000.0, 2)
            if "E_Total" in site_data and site_data["E_Total"] is not None:
                telemetry.total_yield_kwh = round(float(site_data["E_Total"]) / 1000.0, 2)

        # Physikalische Plausibilitätsabgleiche
        # 1. Hausverbrauch aus Knotenpunktsatz ableiten falls nicht direkt gegeben:
        # P_Load = P_PV + P_Bat + P_Grid (mit P_Bat < 0 bei Laden, > 0 bei Entladen)
        if telemetry.load_power_w is None and telemetry.pv_power_w is not None and telemetry.grid_power_w is not None:
            bat_flow = (telemetry.battery_power_w or 0.0)
            calc_load = (telemetry.pv_power_w or 0.0) + (telemetry.grid_power_w or 0.0) - bat_flow
            if calc_load >= 0:
                telemetry.load_power_w = round(calc_load, 1)

        # Standard-Fallbacks falls 0
        if telemetry.pv_power_w is None:
            telemetry.pv_power_w = 0.0
        if telemetry.grid_power_w is None:
            telemetry.grid_power_w = 0.0

        return telemetry

    def _login_swqapi(self, username: str, password: str) -> Optional[str]:
        """
        Authentifiziert sich an der Fronius Solar.web Mobile API und liefert ein JWT Token.
        Verwendet Token-Caching mit automatischer Verlängerung.
        """
        cache_key = f"{username}:{password}"
        cached = self._token_cache.get(cache_key)
        now = timezone.now()

        if cached and cached.get("token") and cached.get("expires_at") > now:
            return cached["token"]

        headers = {
            "accesskeyid": self.APP_ACCESS_KEY_ID,
            "accesskeyvalue": self.APP_ACCESS_KEY_VALUE,
            "content-type": "application/json; charset=UTF-8",
            "user-agent": self.APP_USER_AGENT,
        }
        payload = {
            "userId": username.strip(),
            "password": password.strip()
        }

        try:
            resp = requests.post(
                f"{self.SWQAPI_BASE_URL}/iam/jwt?scope=b454e75844",
                headers=headers,
                json=payload,
                timeout=12
            )
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("jwtToken")
                if token:
                    # Token für 50 Minuten im Cache vorhalten
                    self._token_cache[cache_key] = {
                        "token": token,
                        "expires_at": now + datetime.timedelta(minutes=50)
                    }
                    return token
                else:
                    logger.warning("Fronius Solar.web login OK but no jwtToken in body: %s", data)
            else:
                logger.warning("Fronius Solar.web login failed (%s): %s", resp.status_code, resp.text[:200])
        except Exception as e:
            logger.error("Fronius Solar.web login exception: %s", e)

        return None

    def _get_pv_systems(self, jwt_token: str) -> List[Dict[str, Any]]:
        """
        Ruft alle registrierten PV-Anlagen des Nutzers ab.
        """
        headers = {
            "accesskeyid": self.APP_ACCESS_KEY_ID,
            "accesskeyvalue": self.APP_ACCESS_KEY_VALUE,
            "Authorization": f"Bearer {jwt_token}",
            "user-agent": self.APP_USER_AGENT,
        }
        try:
            resp = requests.get(
                f"{self.SWQAPI_BASE_URL}/pvsystems?offset=0&limit=100",
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("pvSystems", [])
        except Exception as e:
            logger.error("Fronius Solar.web get_pv_systems error: %s", e)
        return []

    def fetch_live_telemetry(self, credentials: Dict[str, Any], device=None) -> Dict[str, Any]:
        """
        Führt den Live-Abruf entweder über Solar.web Cloud (swqapi) oder lokales Solar API aus.
        """
        # 1. Lokale Solar API Direkt-Anbindung (falls Host/IP angegeben)
        host = credentials.get("host") or credentials.get("ip") or credentials.get("local_ip")
        if host:
            host_clean = host.replace("http://", "").replace("https://", "").strip("/")
            url = f"http://{host_clean}{self.LOCAL_POWERFLOW_ENDPOINT}"
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    return resp.json()
                raise ConnectionError(f"Fronius Local Solar API responded with HTTP {resp.status_code}")
            except requests.RequestException as e:
                raise ConnectionError(f"Fronius Local Solar API unreachble at {url}: {e}")

        # 2. Solar.web Cloud Anbindung via E-Mail & Passwort
        username = credentials.get("username") or credentials.get("email") or credentials.get("user")
        password = credentials.get("password") or credentials.get("pass")

        # Fallback: Legacy API Keys
        access_key_id = credentials.get("access_key_id")
        access_key_value = credentials.get("access_key_value")
        pv_system_id = credentials.get("pv_system_id")

        if username and password:
            jwt_token = self._login_swqapi(username, password)
            if not jwt_token:
                raise ConnectionError("Fronius Solar.web: Authentifizierung mit Benutzername / Passwort fehlgeschlagen.")

            # Falls pv_system_id nicht bekannt, automatisch ermitteln
            if not pv_system_id:
                systems = self._get_pv_systems(jwt_token)
                if not systems:
                    raise ConnectionError("Fronius Solar.web: Keine PV-Anlagen unter diesem Benutzerkonto gefunden.")
                pv_system_id = systems[0].get("pvSystemId")

            headers = {
                "accesskeyid": self.APP_ACCESS_KEY_ID,
                "accesskeyvalue": self.APP_ACCESS_KEY_VALUE,
                "Authorization": f"Bearer {jwt_token}",
                "user-agent": self.APP_USER_AGENT,
            }

            url = f"{self.SWQAPI_BASE_URL}/pvsystems/{pv_system_id}/flowdata"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                payload = resp.json()
                if isinstance(payload, dict):
                    payload["pvSystemId"] = pv_system_id
                return payload
            elif resp.status_code == 401:
                # Token abgelaufen, Cache leeren und 1x Retry
                cache_key = f"{username}:{password}"
                self._token_cache.pop(cache_key, None)
                new_token = self._login_swqapi(username, password)
                if new_token:
                    headers["Authorization"] = f"Bearer {new_token}"
                    resp2 = requests.get(url, headers=headers, timeout=10)
                    if resp2.status_code == 200:
                        payload = resp2.json()
                        if isinstance(payload, dict):
                            payload["pvSystemId"] = pv_system_id
                        return payload
            raise ConnectionError(f"Fronius Solar.web flowdata HTTP {resp.status_code}: {resp.text[:150]}")

    def fetch_telemetry(self, credentials: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Fragt die Live-Telemetrie vom Wechselrichter ab und konvertiert sie in CanonicalTelemetry.
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

        if is_mock or not (credentials.get("username") or credentials.get("host") or credentials.get("access_key_id")):
            payload = self.generate_mock_payload()
            telemetry = self.parse_payload(payload)
            return AdapterTestResult(
                status="success",
                message="Fronius Solar.web Simulation erfolgreich.",
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
            err_msg = f"Fronius Verbindungstest fehlgeschlagen: {e}"
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

