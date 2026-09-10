"""Background Telemetry Bridge, Bidirectional Control, 24h Offline-Resilience & Buffer for Sharegy."""

import asyncio
import json
import logging
import random
import sqlite3
import time
from datetime import datetime, timezone
import aiohttp

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    CONF_HOST,
    CONF_WS_URL,
    CONF_HOME_TOKEN,
    CONF_PROTOCOL,
    CONF_BIDIRECTIONAL_ENABLED,
    CONF_GRID_POWER_SENSOR,
    CONF_PV_POWER_SENSOR,
    CONF_BATTERY_POWER_SENSOR,
    CONF_BATTERY_SOC_SENSOR,
    CONF_LOAD_POWER_SENSOR,
    CONF_BWWP_NAME,
    CONF_BWWP_POWER,
    CONF_BWWP_TEMP,
    CONF_BWWP_SWITCH,
    CONF_HEATPUMP_NAME,
    CONF_HEATPUMP_POWER,
    CONF_HEATPUMP_TEMP,
    CONF_HEATPUMP_SWITCH,
    CONF_FLOOR_HEATING_NAME,
    CONF_FLOOR_HEATING_POWER,
    CONF_FLOOR_HEATING_ROOM_TEMP,
    CONF_FLOOR_HEATING_FLOW_TEMP,
    CONF_FLOOR_HEATING_FLOOR_TEMP,
    CONF_FLOOR_HEATING_SWITCH,
    CONF_FLOOR_HEATING_FLOW_SETPOINT,
    CONF_FLOOR_HEATING_TARGET_ROOM_TEMP,
    CONF_FLOOR_HEATING_BOOST_DELTA_K,
    CONF_FLOOR_HEATING_MAX_FLOOR_TEMP,
    CONF_WALLBOX_NAME,
    CONF_WALLBOX_POWER,
    CONF_WALLBOX_SWITCH,
    CONF_SUBMETER_SENSORS,
    CONF_SYNC_INTERVAL,
    DEFAULT_FBH_TARGET_ROOM_TEMP,
    DEFAULT_FBH_BOOST_DELTA_K,
    DEFAULT_FBH_MAX_FLOOR_TEMP,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


class SharegyOfflineBuffer:
    """Persistent SQLite-backed buffer for Store & Forward telemetry and 24h schedule cache."""

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
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS schedule_cache (
                        key TEXT PRIMARY KEY,
                        timeline_json TEXT NOT NULL,
                        updated_at REAL NOT NULL
                    )
                    """
                )
                conn.commit()
        except Exception as err:
            _LOGGER.error("Failed to initialize Sharegy SQLite buffer: %s", err)

    def push(self, payload_dict: dict):
        """Enqueue a telemetry frame when offline."""
        try:
            with sqlite3.connect(self.db_path) as conn:
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

    def save_schedule(self, timeline: list):
        """Persist 24h schedule for offline resilience."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO schedule_cache (key, timeline_json, updated_at) VALUES ('24h_schedule', ?, ?)",
                    (json.dumps(timeline), time.time()),
                )
                conn.commit()
        except Exception as err:
            _LOGGER.warning("Could not persist 24h schedule cache: %s", err)

    def load_schedule(self) -> list:
        """Load persisted 24h schedule."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT timeline_json FROM schedule_cache WHERE key = '24h_schedule'")
                row = cursor.fetchone()
                if row and row[0]:
                    return json.loads(row[0])
        except Exception:
            pass
        return []


class SharegyBridge:
    """Manages WSS connection, live state aggregation, upload, and 24h offline resilience."""

    def __init__(self, hass, entry_data: dict, db_path: str):
        self.hass = hass
        self.entry_data = entry_data
        self.token = entry_data.get(CONF_HOME_TOKEN) or ""
        self.ws_url_config = entry_data.get(CONF_WS_URL) or ""
        self.host = entry_data.get(CONF_HOST, "https://sharegy.de").rstrip("/")
        self.protocol = entry_data.get(CONF_PROTOCOL, "websocket")
        self.bidirectional_enabled = entry_data.get(CONF_BIDIRECTIONAL_ENABLED, True)
        self.buffer = SharegyOfflineBuffer(db_path)
        self.is_connected = False
        self.offline_autonomous = False
        self._running = False
        self._ws_session = None
        self._ws = None
        self._task = None
        self._offline_task = None
        self._unsub_listeners = []
        self._reconnect_attempts = 0

        # Real-time state received from Sharegy
        self.flow_temp_setpoint_c = 30.0
        self.screed_soc_pct = 50.0
        self.operating_mode = "STANDBY"
        self.spot_price_ct = 15.0
        self.last_heartbeat = time.time()
        self.cached_schedule_24h = self.buffer.load_schedule()

    def get_effective_ws_url(self) -> str:
        """Resolve full WebSocket URL."""
        if self.ws_url_config and self.ws_url_config.strip().startswith("wss://"):
            url = self.ws_url_config.strip()
            base = url if url.endswith("/") else f"{url}/"
        else:
            base = f"wss://sharegy.de/ws/energy/{self.token}/"

        if "?" not in base:
            base += "?client=homeassistant&source=homeassistant&version=2.1.0"
        return base

    async def start(self):
        """Start the background streaming worker and state change listeners."""
        self._running = True
        self._setup_control_listeners()
        self._task = asyncio.create_task(self._main_loop())
        self._offline_task = asyncio.create_task(self._offline_heating_loop())

    async def stop(self):
        """Stop worker and close connections."""
        self._running = False
        for unsub in self._unsub_listeners:
            unsub()
        self._unsub_listeners.clear()

        if self._ws:
            await self._ws.close()
        if self._ws_session:
            await self._ws_session.close()
        if self._task:
            self._task.cancel()
        if self._offline_task:
            self._offline_task.cancel()

    def _setup_control_listeners(self):
        """Listen to state changes on control switches for closed-loop status feedback."""
        tracked_switches = [
            (self.entry_data.get(CONF_BWWP_SWITCH), self.entry_data.get(CONF_BWWP_NAME, "Brauchwasser")),
            (self.entry_data.get(CONF_HEATPUMP_SWITCH), self.entry_data.get(CONF_HEATPUMP_NAME, "Waermepumpe")),
            (self.entry_data.get(CONF_FLOOR_HEATING_SWITCH), self.entry_data.get(CONF_FLOOR_HEATING_NAME, "Fussbodenheizung")),
            (self.entry_data.get(CONF_WALLBOX_SWITCH), self.entry_data.get(CONF_WALLBOX_NAME, "Wallbox")),
        ]

        for ent_id, identifier in tracked_switches:
            if ent_id:
                def make_handler(ident):
                    @callback
                    def _handler(event):
                        new_state = event.data.get("new_state")
                        if not new_state:
                            return
                        is_on = (new_state.state.lower() in ("on", "true", "1"))
                        now_sec = int(time.time())
                        payload = {
                            "identifier": ident,
                            "device": ident,
                            "id": ident,
                            "state": is_on,
                            "relay_state": is_on,
                            "val": is_on,
                            "role": "consumer",
                            "metric": "relay_state",
                            "ts": now_sec,
                            "source": "homeassistant_feedback",
                        }
                        if self.is_connected and self._ws and not self._ws.closed:
                            asyncio.create_task(self._ws.send_str(json.dumps(payload)))
                        else:
                            self.buffer.push(payload)
                    return _handler

                unsub = async_track_state_change_event(
                    self.hass, [ent_id], make_handler(identifier)
                )
                self._unsub_listeners.append(unsub)

    async def _main_loop(self):
        """Continuous connection & sync loop with exponential backoff and watchdog."""
        while self._running:
            try:
                if self.protocol == "websocket":
                    await self._run_websocket_stream()
                else:
                    await self._run_rest_sync()
            except asyncio.CancelledError:
                break
            except Exception as err:
                self.is_connected = False
                self._reconnect_attempts += 1
                # Exponential backoff: 2s -> 3s -> 4.5s -> 6.75s ... max 25s
                backoff = min(25.0, 2.0 * (1.5 ** min(self._reconnect_attempts - 1, 7)))
                jitter = random.uniform(0.0, 0.5)
                delay = round(backoff + jitter, 1)
                _LOGGER.warning(
                    "Sharegy connection error: %s. Retrying in %.1fs (Attempt #%d)...",
                    err,
                    delay,
                    self._reconnect_attempts,
                )
                await asyncio.sleep(delay)

    async def _run_websocket_stream(self):
        """Maintain persistent WSS connection, receive commands, and stream telemetry."""
        ws_url = self.get_effective_ws_url()
        _LOGGER.info("Connecting to Sharegy WebSocket at %s", ws_url)

        self._ws_session = aiohttp.ClientSession()
        async with self._ws_session.ws_connect(
            ws_url, heartbeat=15.0, timeout=10.0
        ) as ws:
            self._ws = ws
            self.is_connected = True
            self.offline_autonomous = False
            self._reconnect_attempts = 0
            self.last_heartbeat = time.time()
            _LOGGER.info("Connected to Sharegy WebSocket successfully!")

            # 1. Flush any pending offline buffer first
            await self._flush_buffer_ws(ws)

            # 2. Start concurrent listener for incoming commands from Sharegy
            cmd_task = asyncio.create_task(self._listen_incoming_commands(ws))
            watchdog_task = asyncio.create_task(self._heartbeat_watchdog(ws))

            # 3. Main telemetry sync loop
            try:
                while self._running and not ws.closed:
                    packets = self._collect_discrete_packets()
                    for packet in packets:
                        try:
                            await ws.send_str(json.dumps(packet))
                        except Exception as send_err:
                            _LOGGER.warning("WebSocket send failed, buffering: %s", send_err)
                            self.buffer.push(packet)

                    if self.buffer.count_pending() > 0:
                        await self._flush_buffer_ws(ws)

                    sync_interval = max(1, int(self.entry_data.get(CONF_SYNC_INTERVAL, 5)))
                    await asyncio.sleep(sync_interval)
            finally:
                cmd_task.cancel()
                watchdog_task.cancel()

    async def _heartbeat_watchdog(self, ws):
        """Send explicit ping frames and verify connection health."""
        try:
            while self._running and not ws.closed:
                await asyncio.sleep(15)
                now = time.time()
                try:
                    await ws.send_str(json.dumps({"method": "ping"}))
                except Exception:
                    pass

                if self.last_heartbeat > 0 and (now - self.last_heartbeat > 40.0):
                    _LOGGER.warning("Sharegy WebSocket heartbeat watchdog timeout (>40s). Forcing reconnect...")
                    await ws.close()
                    break
        except asyncio.CancelledError:
            pass

    async def _listen_incoming_commands(self, ws):
        """Receive switch/control commands, schedules and setpoints from Sharegy."""
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    self.last_heartbeat = time.time()
                    data = json.loads(msg.data)
                    await self._handle_incoming_command(data)
                except Exception as err:
                    _LOGGER.warning("Error parsing Sharegy command: %s", err)
            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                break

    async def _handle_incoming_command(self, data: dict):
        """Execute control command, update setpoints and cache 24h schedule."""
        self.last_heartbeat = time.time()
        _LOGGER.debug("Received control message from Sharegy: %s", data)

        # 1. 24h MPC Schedule Caching
        timeline = data.get("timeline") or data.get("predictive_mpc", {}).get("timeline")
        if isinstance(timeline, list) and len(timeline) > 0:
            self.cached_schedule_24h = timeline
            self.buffer.save_schedule(timeline)
            _LOGGER.info("Cached 24h predictive heating schedule (%d slots) in Home Assistant.", len(timeline))

        # 2. Update setpoints and state metrics
        if "flow_temp_setpoint_c" in data:
            self.flow_temp_setpoint_c = float(data["flow_temp_setpoint_c"])
            # If setpoint entity configured (e.g. number or input_number), update it
            sp_entity = self.entry_data.get(CONF_FLOOR_HEATING_FLOW_SETPOINT)
            if sp_entity:
                domain = sp_entity.split(".")[0]
                await self.hass.services.async_call(
                    domain, "set_value", {"entity_id": sp_entity, "value": self.flow_temp_setpoint_c}
                )

        if "screed_soc_pct" in data:
            self.screed_soc_pct = float(data["screed_soc_pct"])
        if "mode" in data:
            self.operating_mode = str(data["mode"])
        if "spot_price_ct" in data:
            self.spot_price_ct = float(data["spot_price_ct"])

        # Check if bidirectional control is active
        if not self.bidirectional_enabled:
            _LOGGER.debug("Bidirectional control is paused in Home Assistant.")
            return

        identifier = (data.get("identifier") or data.get("device") or data.get("src") or "").strip()
        raw_val = data.get("val") if "val" in data else (data.get("value") if "value" in data else data.get("relay_state"))

        # Map identifier to HA Switch Entity
        target_entity = None
        if identifier == self.entry_data.get(CONF_BWWP_NAME, "Brauchwasser") or "bwwp_boost" in data:
            target_entity = self.entry_data.get(CONF_BWWP_SWITCH)
            if "bwwp_boost" in data:
                raw_val = data["bwwp_boost"]
        elif identifier == self.entry_data.get(CONF_HEATPUMP_NAME, "Waermepumpe"):
            target_entity = self.entry_data.get(CONF_HEATPUMP_SWITCH)
        elif identifier in (self.entry_data.get(CONF_FLOOR_HEATING_NAME, "Fussbodenheizung"), "floor_heating", "floor_heating_relay") or "floor_heating_boost" in data or data.get("action") == "FLOOR_HEATING_BOOST":
            target_entity = self.entry_data.get(CONF_FLOOR_HEATING_SWITCH)
            if "floor_heating_boost" in data:
                raw_val = data["floor_heating_boost"]
            elif data.get("action") == "FLOOR_HEATING_BOOST":
                raw_val = True
        elif identifier == self.entry_data.get(CONF_WALLBOX_NAME, "Wallbox"):
            target_entity = self.entry_data.get(CONF_WALLBOX_SWITCH)

        # Fallback for Shelly RPC Switch.Set
        if not target_entity and data.get("method", "").startswith("Switch."):
            on_val = data.get("params", {}).get("on")
            raw_val = on_val
            target_entity = self.entry_data.get(CONF_FLOOR_HEATING_SWITCH) or self.entry_data.get(CONF_BWWP_SWITCH) or self.entry_data.get(CONF_HEATPUMP_SWITCH)

        if target_entity:
            bool_val = (raw_val is True or raw_val == 1 or str(raw_val).lower() in ("true", "1", "on"))
            service = "turn_on" if bool_val else "turn_off"
            domain = target_entity.split(".")[0]
            _LOGGER.info("Executing Sharegy Switch: %s.%s on %s", domain, service, target_entity)
            await self.hass.services.async_call(
                domain, service, {"entity_id": target_entity}, blocking=True
            )

    async def _offline_heating_loop(self):
        """Autonomous 24h Offline-Resilience Controller Loop (Runs every 60s)."""
        while self._running:
            try:
                await asyncio.sleep(60)

                # If online, cloud handles live optimization
                if self.is_connected:
                    self.offline_autonomous = False
                    continue

                fh_switch = self.entry_data.get(CONF_FLOOR_HEATING_SWITCH)
                fh_room_temp_id = self.entry_data.get(CONF_FLOOR_HEATING_ROOM_TEMP)

                if not fh_switch or not fh_room_temp_id:
                    continue

                self.offline_autonomous = True

                # Read current room temperature
                state_obj = self.hass.states.get(fh_room_temp_id)
                if not state_obj or state_obj.state in ("unknown", "unavailable", "None", ""):
                    continue

                try:
                    current_temp = float(state_obj.state)
                except (ValueError, TypeError):
                    continue

                target_temp = float(self.entry_data.get(CONF_FLOOR_HEATING_TARGET_ROOM_TEMP, DEFAULT_FBH_TARGET_ROOM_TEMP))
                boost_delta = float(self.entry_data.get(CONF_FLOOR_HEATING_BOOST_DELTA_K, DEFAULT_FBH_BOOST_DELTA_K))
                max_floor_temp = float(self.entry_data.get(CONF_FLOOR_HEATING_MAX_FLOOR_TEMP, DEFAULT_FBH_MAX_FLOOR_TEMP))

                current_hour = datetime.now().hour
                hour_label = f"{current_hour:02d}:00"

                # Match slot from cached schedule
                current_slot = None
                if self.cached_schedule_24h:
                    current_slot = next((s for s in self.cached_schedule_24h if s.get("hour_label") == hour_label), self.cached_schedule24h[0] if self.cached_schedule_24h else None)

                should_heat = False
                if current_temp >= max_floor_temp:
                    should_heat = False
                elif current_temp < (target_temp - 0.5):
                    should_heat = True
                elif current_slot:
                    action = current_slot.get("action_mode", "heat")
                    if action == "preheat":
                        should_heat = (current_temp < (target_temp + boost_delta))
                    elif action == "coast":
                        should_heat = False
                    elif action == "heat":
                        should_heat = (current_temp < target_temp)
                    else:
                        should_heat = False
                else:
                    should_heat = (current_temp < target_temp)

                domain = fh_switch.split(".")[0]
                service = "turn_on" if should_heat else "turn_off"
                _LOGGER.info(
                    "[HA Offline-Resilience 🛡️] Autonomously controlling floor heating: Room=%.1f°C, Action=%s -> %s.%s",
                    current_temp,
                    current_slot.get("action_mode", "thermostat") if current_slot else "thermostat",
                    domain,
                    service,
                )
                await self.hass.services.async_call(
                    domain, service, {"entity_id": fh_switch}, blocking=True
                )

                # Set flow temp setpoint if configured
                sp_entity = self.entry_data.get(CONF_FLOOR_HEATING_FLOW_SETPOINT)
                if sp_entity and current_slot and current_slot.get("opt_flow_temp_c"):
                    sp_val = float(current_slot["opt_flow_temp_c"])
                    sp_domain = sp_entity.split(".")[0]
                    await self.hass.services.async_call(
                        sp_domain, "set_value", {"entity_id": sp_entity, "value": sp_val}
                    )

            except asyncio.CancelledError:
                break
            except Exception as loop_err:
                _LOGGER.debug("Error in offline heating loop: %s", loop_err)

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

    def _collect_discrete_packets(self) -> list[dict]:
        """Read states from configured HA entities and build individual discrete packets."""
        packets = []
        now_sec = int(time.time())

        def _get_float_val(entity_id):
            if not entity_id:
                return None
            state = self.hass.states.get(entity_id)
            if state and state.state not in ("unknown", "unavailable", "None", ""):
                try:
                    return float(state.state)
                except (ValueError, TypeError):
                    return None
            return None

        # 1. EMS Standard Roles
        grid_p = _get_float_val(self.entry_data.get(CONF_GRID_POWER_SENSOR))
        if grid_p is not None:
            packets.append({
                "identifier": "grid",
                "metric": "power",
                "unit": "W",
                "role": "grid",
                "val": grid_p,
                "value": grid_p,
                "ts": now_sec,
                "source": "homeassistant",
            })

        pv_p = _get_float_val(self.entry_data.get(CONF_PV_POWER_SENSOR))
        if pv_p is not None:
            packets.append({
                "identifier": "pv",
                "metric": "power",
                "unit": "W",
                "role": "producer",
                "val": pv_p,
                "value": pv_p,
                "ts": now_sec,
                "source": "homeassistant",
            })

        bat_p = _get_float_val(self.entry_data.get(CONF_BATTERY_POWER_SENSOR))
        if bat_p is not None:
            packets.append({
                "identifier": "battery",
                "metric": "power",
                "unit": "W",
                "role": "battery",
                "val": bat_p,
                "value": bat_p,
                "ts": now_sec,
                "source": "homeassistant",
            })

        bat_soc = _get_float_val(self.entry_data.get(CONF_BATTERY_SOC_SENSOR))
        if bat_soc is not None:
            packets.append({
                "identifier": "battery",
                "metric": "soc",
                "unit": "%",
                "role": "battery",
                "val": max(0.0, min(100.0, bat_soc)),
                "value": max(0.0, min(100.0, bat_soc)),
                "ts": now_sec,
                "source": "homeassistant",
            })

        load_p = _get_float_val(self.entry_data.get(CONF_LOAD_POWER_SENSOR))
        if load_p is not None:
            packets.append({
                "identifier": "house",
                "metric": "power",
                "unit": "W",
                "role": "consumer",
                "val": load_p,
                "value": load_p,
                "ts": now_sec,
                "source": "homeassistant",
            })

        # 2. BWWP (Brauchwasser) Bundle
        bwwp_name = self.entry_data.get(CONF_BWWP_NAME, "Brauchwasser").strip()
        bwwp_p = _get_float_val(self.entry_data.get(CONF_BWWP_POWER))
        if bwwp_p is not None:
            packets.append({
                "identifier": bwwp_name,
                "device": bwwp_name,
                "id": bwwp_name,
                "metric": "power",
                "unit": "W",
                "role": "consumer",
                "val": bwwp_p,
                "value": bwwp_p,
                "ts": now_sec,
                "source": "homeassistant",
            })

        bwwp_t = _get_float_val(self.entry_data.get(CONF_BWWP_TEMP))
        if bwwp_t is not None:
            packets.append({
                "identifier": bwwp_name,
                "device": bwwp_name,
                "id": bwwp_name,
                "metric": "temperature",
                "unit": "°C",
                "role": "sensor",
                "val": bwwp_t,
                "value": bwwp_t,
                "ts": now_sec,
                "source": "homeassistant",
            })

        # 3. Floor Heating (Fußbodenheizung & Estrich-Speicher) Bundle
        fh_name = self.entry_data.get(CONF_FLOOR_HEATING_NAME, "Fussbodenheizung").strip()
        fh_p = _get_float_val(self.entry_data.get(CONF_FLOOR_HEATING_POWER))
        if fh_p is not None:
            packets.append({
                "identifier": fh_name,
                "device": fh_name,
                "id": fh_name,
                "metric": "power",
                "unit": "W",
                "role": "consumer",
                "val": fh_p,
                "value": fh_p,
                "ts": now_sec,
                "source": "homeassistant",
            })

        fh_room_t = _get_float_val(self.entry_data.get(CONF_FLOOR_HEATING_ROOM_TEMP))
        if fh_room_t is not None:
            packets.append({
                "identifier": "floor_heating_room_temp",
                "device": fh_name,
                "id": fh_name,
                "metric": "temperature",
                "unit": "°C",
                "role": "sensor",
                "val": fh_room_t,
                "value": fh_room_t,
                "ts": now_sec,
                "source": "homeassistant",
            })

        fh_flow_t = _get_float_val(self.entry_data.get(CONF_FLOOR_HEATING_FLOW_TEMP))
        if fh_flow_t is not None:
            packets.append({
                "identifier": "floor_heating_flow_temp",
                "device": fh_name,
                "id": fh_name,
                "metric": "temperature",
                "unit": "°C",
                "role": "sensor",
                "val": fh_flow_t,
                "value": fh_flow_t,
                "ts": now_sec,
                "source": "homeassistant",
            })

        fh_floor_t = _get_float_val(self.entry_data.get(CONF_FLOOR_HEATING_FLOOR_TEMP))
        if fh_floor_t is not None:
            packets.append({
                "identifier": "floor_heating_surface_temp",
                "device": fh_name,
                "id": fh_name,
                "metric": "temperature",
                "unit": "°C",
                "role": "sensor",
                "val": fh_floor_t,
                "value": fh_floor_t,
                "ts": now_sec,
                "source": "homeassistant",
            })

        # 4. Heatpump Bundle
        hp_name = self.entry_data.get(CONF_HEATPUMP_NAME, "Waermepumpe").strip()
        hp_p = _get_float_val(self.entry_data.get(CONF_HEATPUMP_POWER))
        if hp_p is not None:
            packets.append({
                "identifier": hp_name,
                "device": hp_name,
                "id": hp_name,
                "metric": "power",
                "unit": "W",
                "role": "consumer",
                "val": hp_p,
                "value": hp_p,
                "ts": now_sec,
                "source": "homeassistant",
            })

        hp_t = _get_float_val(self.entry_data.get(CONF_HEATPUMP_TEMP))
        if hp_t is not None:
            packets.append({
                "identifier": hp_name,
                "device": hp_name,
                "id": hp_name,
                "metric": "temperature",
                "unit": "°C",
                "role": "sensor",
                "val": hp_t,
                "value": hp_t,
                "ts": now_sec,
                "source": "homeassistant",
            })

        # 5. Wallbox Bundle
        wb_name = self.entry_data.get(CONF_WALLBOX_NAME, "Wallbox").strip()
        wb_p = _get_float_val(self.entry_data.get(CONF_WALLBOX_POWER))
        if wb_p is not None:
            packets.append({
                "identifier": wb_name,
                "device": wb_name,
                "id": wb_name,
                "metric": "power",
                "unit": "W",
                "role": "consumer",
                "val": wb_p,
                "value": wb_p,
                "ts": now_sec,
                "source": "homeassistant",
            })

        # 6. Other Submeters & Individual Sensors
        submeters = self.entry_data.get(CONF_SUBMETER_SENSORS, [])
        if isinstance(submeters, list):
            for ent_id in submeters:
                val = _get_float_val(ent_id)
                if val is not None:
                    state_obj = self.hass.states.get(ent_id)
                    unit = state_obj.attributes.get("unit_of_measurement", "W") if state_obj else "W"
                    ident = ent_id.split(".")[-1]
                    metric = "temperature" if "°c" in unit.lower() else ("energy" if "kwh" in unit.lower() else "power")

                    packets.append({
                        "identifier": ident,
                        "device": ident,
                        "id": ident,
                        "metric": metric,
                        "unit": unit,
                        "role": "sensor" if metric == "temperature" else "consumer",
                        "val": val,
                        "value": val,
                        "ts": now_sec,
                        "source": "homeassistant",
                    })

        return packets
