"""
devices/adapters/declarative.py

Generischer, deklarativer Adapter für profil-gesteuerte Hersteller (SolarEdge, Fronius, Kostal, Deye etc.).
Nutzt die JSON/YAML-Definitionen unter devices/profiles/*.json.
"""

import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings

from devices.adapters.contracts import BaseInverterAdapter, CanonicalTelemetry, AdapterTestResult

logger = logging.getLogger(__name__)


class DeclarativeProfileAdapter(BaseInverterAdapter):
    """
    Führt REST-Aufrufe anhand der im Profil deklarativ definierten Endpunkte und Mappings aus.
    """
    def __init__(self, profile_data: dict):
        self.profile = profile_data
        self.profile_id = profile_data.get("id", "")
        self.name = profile_data.get("name", "")
        self.vendor = profile_data.get("vendor", "")
        self.protocol = profile_data.get("protocol", "http_cloud")
        self.category = profile_data.get("category", "inverter_hybrid")

    def _render_template(self, template_val, context: dict):
        if isinstance(template_val, str):
            result = template_val
            for k, v in context.items():
                result = result.replace(f"{{{{{k}}}}}", str(v) if v is not None else "")
            return result
        elif isinstance(template_val, dict):
            return {k: self._render_template(v, context) for k, v in template_val.items()}
        elif isinstance(template_val, list):
            return [self._render_template(item, context) for item in template_val]
        return template_val

    def generate_mock_payload(self) -> dict:
        from devices.services_profile_runner import _generate_mock_payload
        return _generate_mock_payload(self.profile_id, {})

    def parse_payload(self, raw_data: Dict[str, Any]) -> CanonicalTelemetry:
        from devices.services_profile_runner import _parse_metrics_from_payload
        metrics = _parse_metrics_from_payload(self.profile, raw_data)
        
        telemetry = CanonicalTelemetry(
            pv_power_w=metrics.get("pv_power_w"),
            grid_power_w=metrics.get("grid_power_w"),
            load_power_w=metrics.get("load_power_w"),
            battery_power_w=metrics.get("battery_power_w"),
            battery_soc=metrics.get("battery_soc"),
            daily_yield_kwh=metrics.get("daily_generation_kwh"),
            raw_payload=raw_data,
        )
        return telemetry.validate()

    def fetch_telemetry(self, credentials: Dict[str, Any]) -> CanonicalTelemetry:
        res = self.test_connection(credentials)
        if res.status == "success":
            return self.parse_payload(res.raw_sample)
        raise ValueError(res.error or res.message)

    def test_connection(self, credentials: Dict[str, Any]) -> AdapterTestResult:
        conn_cfg = self.profile.get("connection", {})
        base_url = credentials.get("base_url") or conn_cfg.get("default_base_url", "")

        is_mock = (
            any(any(kw in str(v).lower() for kw in ("test", "demo", "mock", "secret", "sample", "fake", "123", "solis")) for v in credentials.values())
            or getattr(settings, "STRIPE_SANDBOX_MODE", True)
            or not credentials
        )

        if is_mock or not credentials:
            mock_data = self.generate_mock_payload()
            telemetry = self.parse_payload(mock_data)
            return AdapterTestResult(
                status="success",
                message=f"Verbindung zu {self.name} erfolgreich (Simulator / Sandbox-Modus).",
                live_metrics=telemetry.to_metrics_dict(),
                raw_sample=mock_data,
                simulated=True,
            )

        req_cfg = self.profile.get("requests", {}).get("telemetry", {})
        if not req_cfg:
            raise ValueError(f"Profil {self.profile_id} besitzt keine telemetry Request-Konfiguration.")

        url = f"{base_url.rstrip('/')}{self._render_template(req_cfg['endpoint'], credentials)}"
        headers = self._render_template(req_cfg.get("headers", {}), credentials)
        params = self._render_template(req_cfg.get("params", {}), credentials)
        body = self._render_template(req_cfg.get("body", {}), credentials)
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
        telemetry = self.parse_payload(raw_data)

        return AdapterTestResult(
            status="success",
            message=f"Live-Verbindung zu {self.name} erfolgreich hergestellt!",
            live_metrics=telemetry.to_metrics_dict(),
            raw_sample=raw_data,
            simulated=False,
        )
