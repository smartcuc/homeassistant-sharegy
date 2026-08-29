"""Background Telemetry Bridge & Offline Buffer for Sharegy."""

import asyncio
import json
import logging
import sqlite3
import time
from datetime import datetime, timezone
import aiohttp

_LOGGER = logging.getLogger(__name__)


class SharegyOfflineBuffer:
    """Persistent SQLite-backed buffer for Store & Forward telemetry."""

    def __init__(self, db_path: str, max_records: int = 100000):
        self.db_path = db_path
        self.max_records = max_records
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telemetry_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        payload TEXT NOT NULL,
                        created_at REAL NOT NULL
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_telemetry_created ON telemetry_queue(created_at)"
                )
                conn.commit()
        except Exception as err:
            _LOGGER.error("Failed to initialize Sharegy SQLite buffer: %s", err)

    def push(self, payload_dict: dict):
        """Enqueue a telemetry frame when offline."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Evict oldest if exceeding capacity
                conn.execute(
                    """
                    DELETE FROM telemetry_queue 
                    WHERE id IN (
                        SELECT id FROM telemetry_queue 
                        ORDER BY id ASC 
                        LIMIT MAX(0, (SELECT COUNT(*) FROM telemetry_queue) - ?)
                    )
                    """,
                    (self.max_records,),
                )
                conn.execute(
                    "INSERT INTO telemetry_queue (payload, created_at) VALUES (?, ?)",
                    (json.dumps(payload_dict), time.time()),
                )
                conn.commit()
        except Exception as err:
            _LOGGER.warning("Could not buffer telemetry locally: %s", err)

    def fetch_batch(self, batch_size: int = 50) -> list[tuple[int, dict]]:
        """Fetch oldest pending batch."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, payload FROM telemetry_queue ORDER BY id ASC LIMIT ?",
                    (batch_size,),
                )
                rows = cursor.fetchall()
                return [(row[0], json.loads(row[1])) for row in rows]
        except Exception as err:
            _LOGGER.error("Error reading from Sharegy local buffer: %s", err)
            return []

    def ack_batch(self, ids: list[int]):
        """Remove successfully transmitted records."""
        if not ids:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                placeholders = ",".join("?" for _ in ids)
                conn.execute(
                    f"DELETE FROM telemetry_queue WHERE id IN ({placeholders})", ids
                )
                conn.commit()
        except Exception as err:
            _LOGGER.error("Error clearing buffered items: %s", err)

    def count_pending(self) -> int:
        """Count pending records in buffer."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM telemetry_queue")
                row = cursor.fetchone()
                return row[0] if row else 0
        except Exception:
            return 0


class SharegyBridge:
    """Manages connection, live state aggregation, and upload to Sharegy."""

    def __init__(self, hass, entry_data: dict, db_path: str):
        self.hass = hass
        self.entry_data = entry_data
        self.token = entry_data.get("home_token")
        self.host = entry_data.get("host", "https://sharegy.de").rstrip("/")
        self.protocol = entry_data.get("protocol", "websocket")
        self.buffer = SharegyOfflineBuffer(db_path)
        self.is_connected = False
        self._running = False
        self._ws_session = None
        self._ws = None
        self._task = None

    async def start(self):
        """Start the background streaming worker."""
        self._running = True
        self._task = asyncio.create_task(self._main_loop())

    async def stop(self):
        """Stop worker and close connections."""
        self._running = False
        if self._ws:
            await self._ws.close()
        if self._ws_session:
            await self._ws_session.close()
        if self._task:
            self._task.cancel()

    async def _main_loop(self):
        """Continuous connection & sync loop."""
        while self._running:
            try:
                if self.protocol == "websocket":
                    await self._run_websocket_stream()
                else:
                    await self._run_rest_sync()
            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.warning("Sharegy connection error: %s. Retrying in 10s...", err)
                self.is_connected = False
                await asyncio.sleep(10)

    async def _run_websocket_stream(self):
        """Maintain persistent WSS connection and flush queue."""
        ws_url = f"{self.host.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/energy/{self.token}/"
        _LOGGER.info("Connecting to Sharegy WebSocket at %s", ws_url)

        self._ws_session = aiohttp.ClientSession()
        async with self._ws_session.ws_connect(
            ws_url, heartbeat=25.0, timeout=15.0
        ) as ws:
            self._ws = ws
            self.is_connected = True
            _LOGGER.info("Connected to Sharegy WebSocket successfully!")

            # 1. Flush any pending offline buffer first
            await self._flush_buffer_ws(ws)

            # 2. Main collection & stream loop
            while self._running and not ws.closed:
                payload = self._collect_telemetry_payload()
                if payload:
                    try:
                        await ws.send_str(json.dumps(payload))
                    except Exception as send_err:
                        _LOGGER.warning("WebSocket send failed, buffering: %s", send_err)
                        self.buffer.push(payload)
                        break

                # Flush backlog if available
                if self.buffer.count_pending() > 0:
                    await self._flush_buffer_ws(ws)

                sync_interval = self.entry_data.get("sync_interval", 5)
                await asyncio.sleep(sync_interval)

    async def _flush_buffer_ws(self, ws):
        """Transmit buffered backlog over WebSocket."""
        pending = self.buffer.fetch_batch(batch_size=50)
        while pending and self._running and not ws.closed:
            acked_ids = []
            for record_id, payload in pending:
                try:
                    await ws.send_str(json.dumps(payload))
                    acked_ids.append(record_id)
                except Exception:
                    break
            self.buffer.ack_batch(acked_ids)
            if len(acked_ids) < len(pending):
                break
            pending = self.buffer.fetch_batch(batch_size=50)

    async def _run_rest_sync(self):
        """Fallback HTTP POST sync."""
        self._ws_session = aiohttp.ClientSession()
        while self._running:
            payload = self._collect_telemetry_payload()
            if payload:
                try:
                    url = f"{self.host}/api/v1/metrics/"
                    headers = {
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json",
                    }
                    async with self._ws_session.post(
                        url, json=payload, headers=headers, timeout=10.0
                    ) as resp:
                        if resp.status in (200, 201, 202):
                            self.is_connected = True
                        else:
                            self.buffer.push(payload)
                            self.is_connected = False
                except Exception as err:
                    _LOGGER.warning("REST push failed, buffering: %s", err)
                    self.buffer.push(payload)
                    self.is_connected = False

            sync_interval = self.entry_data.get("sync_interval", 5)
            await asyncio.sleep(sync_interval)

    def _collect_telemetry_payload(self) -> dict | None:
        """Read states from selected HA entities and build standard frame."""
        now_iso = datetime.now(timezone.utc).isoformat()
        frame = {
            "source": "homeassistant",
            "timestamp": now_iso,
            "metrics": {},
        }

        # Helper to get float state
        def _get_val(entity_id):
            if not entity_id:
                return None
            state = self.hass.states.get(entity_id)
            if state and state.state not in ("unknown", "unavailable", "None", ""):
                try:
                    return float(state.state)
                except ValueError:
                    return None
            return None

        # 1. Standard Roles
        grid_p = _get_val(self.entry_data.get("grid_power_sensor"))
        if grid_p is not None:
            frame["metrics"]["grid_power_w"] = grid_p

        pv_p = _get_val(self.entry_data.get("pv_power_sensor"))
        if pv_p is not None:
            frame["metrics"]["pv_power_w"] = pv_p

        bat_p = _get_val(self.entry_data.get("battery_power_sensor"))
        if bat_p is not None:
            frame["metrics"]["battery_power_w"] = bat_p

        bat_soc = _get_val(self.entry_data.get("battery_soc_sensor"))
        if bat_soc is not None:
            frame["metrics"]["battery_soc_pct"] = bat_soc

        load_p = _get_val(self.entry_data.get("load_power_sensor"))
        if load_p is not None:
            frame["metrics"]["load_power_w"] = load_p

        # 2. Submeters / Einzelverbraucher
        submeters = self.entry_data.get("submeter_sensors", [])
        if isinstance(submeters, list):
            submeter_data = {}
            for ent_id in submeters:
                val = _get_val(ent_id)
                if val is not None:
                    # Friendly name from entity
                    state_obj = self.hass.states.get(ent_id)
                    name = (
                        state_obj.attributes.get("friendly_name")
                        if state_obj
                        else ent_id
                    )
                    submeter_data[ent_id] = {
                        "name": name,
                        "power_w": val,
                    }
            if submeter_data:
                frame["metrics"]["submeters"] = submeter_data

        return frame if frame["metrics"] else None
