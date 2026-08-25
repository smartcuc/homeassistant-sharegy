# pyright: reportMissingImports=false
"""DataUpdateCoordinator for Sharegy HEMS."""

import asyncio
from datetime import timedelta
import logging
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    ENDPOINT_DASHBOARD,
    ENDPOINT_BALANCE,
    ENDPOINT_OPTIMIZER,
    ENDPOINT_TELEMETRY_PUSH,
)

_LOGGER = logging.getLogger(__name__)


class SharegyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Sharegy data from the API."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        host = str(entry.data.get(CONF_HOST, "")).strip().rstrip("/")
        if not host.startswith(("http://", "https://")):
            if host.startswith("192.168.") or host.startswith("10.") or host.startswith("172.") or host.startswith("localhost") or host.startswith("127.0.0.1"):
                host = f"http://{host}"
            else:
                host = f"https://{host}"
        self.host = host
        self.api_key = str(entry.data.get(CONF_API_KEY, "")).strip()
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    def _get_headers(self) -> dict:
        """Return authorization headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _async_update_data(self) -> dict:
        """Fetch data from Sharegy API endpoints."""
        headers = self._get_headers()
        data = {}

        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                # 1. Fetch Dashboard & Live Telemetry
                dash_url = f"{self.host}{ENDPOINT_DASHBOARD}"
                async with session.get(dash_url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data["dashboard"] = await resp.json()
                    elif resp.status in (401, 403):
                        raise UpdateFailed("Authentifizierungsfehler bei Sharegy. Bitte API-Key prüfen.")
                    else:
                        _LOGGER.warning("Sharegy Dashboard HTTP %s", resp.status)
                        data["dashboard"] = {}

                # 2. Fetch Energy Balance & KPIs
                balance_url = f"{self.host}{ENDPOINT_BALANCE}"
                async with session.get(balance_url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data["balance"] = await resp.json()
                    else:
                        data["balance"] = {}

                # 3. Fetch Optimizer Schedule (1h, 2h, 4h Window)
                opt_url = f"{self.host}{ENDPOINT_OPTIMIZER}"
                async with session.get(opt_url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data["optimizer"] = await resp.json()
                    else:
                        data["optimizer"] = {}

            return data

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Verbindungsfehler zu Sharegy ({self.host}): {err}") from err
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout beim Abruf von Sharegy ({self.host})") from err
        except Exception as err:
            raise UpdateFailed(f"Unerwarteter Fehler: {err}") from err

    async def async_push_telemetry(self, devices_payload: list) -> bool:
        """Push local Home Assistant telemetry data securely to Sharegy."""
        headers = self._get_headers()
        url = f"{self.host}{ENDPOINT_TELEMETRY_PUSH}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={"devices": devices_payload}, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        res_json = await resp.json()
                        _LOGGER.debug("Sharegy telemetry push success: %s", res_json)
                        return True
                    _LOGGER.error("Sharegy telemetry push failed with HTTP %s", resp.status)
                    return False
        except Exception as err:
            _LOGGER.error("Error pushing telemetry to Sharegy: %s", err)
            return False

