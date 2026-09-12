"""
Client library for communicating with moniy (Monitoring our Y's: Sharegy & Factofy)
Carrier, Reverse-RPC Gateway and In-Flight DB-Backup Vault.
"""

import logging
from typing import Any, Dict, Optional
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class MoniyClientError(Exception):
    pass


class MoniyClient:
    """
    Client for Server-to-Server interactions with moniy.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        s2s_api_key: Optional[str] = None,
        tenant_id: str = "sharegy",
    ):
        self.base_url = (base_url or getattr(settings, "MONIY_URL", getattr(settings, "MON_NEXUS_URL", "https://mon.sharegy.de"))).rstrip("/")
        self.s2s_api_key = s2s_api_key or getattr(settings, "MONIY_S2S_KEY", getattr(settings, "MON_NEXUS_S2S_KEY", ""))
        self.tenant_id = tenant_id

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-Moniy-S2S-Key": self.s2s_api_key,
            "X-Nexus-S2S-Key": self.s2s_api_key,  # Backwards compatibility
            "Content-Type": "application/json",
            "User-Agent": "Sharegy-HEMS-Core/1.0",
        }

    def send_rpc(
        self,
        device_sn: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 5.0,
    ) -> Dict[str, Any]:
        """
        Dispatches a Reverse-RPC command to a specific edge device and waits synchronously for the response.

        Example:
            client = MoniyClient()
            res = client.send_rpc(
                device_sn="IOB-0012-B9A1",
                method="eebus.curtail",
                params={"limit_kw": 4.2, "duration_s": 3600},
                timeout=5.0
            )
        """
        endpoint = f"{self.base_url}/api/v1/rpc/dispatch"
        payload = {
            "tenant_id": self.tenant_id,
            "device_sn": device_sn,
            "method": method,
            "params": params or {},
            "timeout": timeout,
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=timeout + 2.0,
            )

            if response.status_code == 401:
                raise MoniyClientError("Authentication failed: Invalid MONIY_S2S_KEY")

            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                err = data.get("error", {})
                logger.warning(
                    f"moniy RPC failed for device {device_sn} ({method}): {err.get('message')} [code: {err.get('code')}]"
                )
                return {
                    "success": False,
                    "error": err,
                    "device_sn": device_sn,
                }

            return {
                "success": True,
                "result": data.get("result"),
                "device_sn": device_sn,
            }

        except requests.exceptions.Timeout:
            logger.error(f"HTTP Timeout contacting moniy endpoint {endpoint} for device {device_sn}")
            return {
                "success": False,
                "error": {"code": -32000, "message": "HTTP Connection to moniy timed out"},
                "device_sn": device_sn,
            }
        except Exception as e:
            logger.error(f"Failed to execute RPC via moniy: {e}", exc_info=True)
            return {
                "success": False,
                "error": {"code": -32603, "message": str(e)},
                "device_sn": device_sn,
            }

    def check_health(self) -> Dict[str, Any]:
        """Checks liveness of the moniy cluster."""
        endpoint = f"{self.base_url}/health"
        try:
            resp = requests.get(endpoint, timeout=3.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"moniy health check failed: {e}")
            return {"status": "unreachable", "error": str(e)}


# Singleton client instance
moniy_client = MoniyClient()
nexus_client = moniy_client  # Alias
