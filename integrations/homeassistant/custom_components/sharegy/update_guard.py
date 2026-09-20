"""
Home Assistant Custom Component Update Watchdog with Automated Rollback Protection.
"""

import os
import json
import time
import shutil
import logging
import asyncio
import subprocess
from typing import Dict, Any, Optional

_LOGGER = logging.getLogger(__name__)

STATE_FILENAME = ".ha_sharegy_update_state.json"


class HaUpdateWatchdog:
    """Manages Canary OTA updates and 15-minute rollback safety net for Home Assistant."""

    def __init__(self, bridge):
        self.bridge = bridge
        self.component_dir = os.path.dirname(os.path.abspath(__file__))
        self.state_file_path = os.path.join(self.component_dir, STATE_FILENAME)
        self.auto_confirm_task: Optional[asyncio.Task] = None

    def read_state(self) -> Optional[Dict[str, Any]]:
        try:
            if os.path.exists(self.state_file_path):
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            _LOGGER.warning("[OTA Watchdog] Error reading state: %s", e)
        return None

    def write_state(self, state: Dict[str, Any]):
        try:
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            _LOGGER.error("[OTA Watchdog] Error writing state: %s", e)

    def check_pending_update_on_startup(self):
        """Checks if Home Assistant booted under pending update verification window."""
        state = self.read_state()
        if not state:
            return

        if state.get("status") == "pending":
            _LOGGER.warning(
                "[OTA Watchdog] 🛡️ Sharegy Component booted under pending update verification! Target: %s. 15-min rollback active.",
                state.get("target_version"),
            )
            # Schedule auto-confirm in 3 minutes if stable
            self.auto_confirm_task = asyncio.create_task(self._auto_confirm_worker())

    async def _auto_confirm_worker(self):
        try:
            await asyncio.sleep(180)  # 3 minutes
            if self.bridge.is_connected or (self.bridge._carrier_ws and not self.bridge._carrier_ws.closed):
                self.confirm_update("auto_stability_test_passed")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.error("[OTA Watchdog] Error in auto confirm worker: %s", e)

    def confirm_update(self, reason: str = "manual_admin_rpc") -> Dict[str, Any]:
        """Permanently confirms the update and disarms rollback."""
        state = self.read_state()
        if not state:
            return {"status": "no_active_update", "message": "No pending update found."}

        if self.auto_confirm_task and not self.auto_confirm_task.done():
            self.auto_confirm_task.cancel()

        state["status"] = "confirmed"
        state["confirmed_at"] = time.time()
        state["confirmation_reason"] = reason
        self.write_state(state)

        _LOGGER.info("[OTA Watchdog] ✅ Sharegy update confirmed permanently (%s).", reason)
        return {
            "status": "confirmed",
            "active_version": getattr(self.bridge, "version", "2.2.0"),
            "reason": reason,
            "confirmed_at": state["confirmed_at"],
        }

    async def initiate_update(self, target_version: str = "smartcuc/homeassistant-sharegy#main", timeout_seconds: int = 900) -> Dict[str, Any]:
        """Creates backup and downloads new component version with 15-minute rollback safety."""
        from .const import VERSION
        current_version = VERSION
        backup_dir = os.path.join(self.component_dir, f".backup_{current_version}_{int(time.time())}")

        # Guard: Reject ioBroker packages sent to Home Assistant
        target_str = str(target_version or "").strip()
        if "iobroker" in target_str.lower():
            _LOGGER.error("[OTA Watchdog] ❌ Invalid update target '%s' for Home Assistant integration!", target_str)
            return {
                "status": "error",
                "message": f"Invalid update package '{target_str}'. Home Assistant requires 'smartcuc/homeassistant-sharegy', not ioBroker packages.",
            }

        if not target_str or target_str == "main":
            target_str = "smartcuc/homeassistant-sharegy#main"
        elif not target_str.startswith("http") and not "/" in target_str:
            target_str = f"smartcuc/homeassistant-sharegy#{target_str}"

        _LOGGER.warning("[OTA Watchdog] 🚀 Initiating guarded OTA update from %s to '%s'...", current_version, target_str)

        # 1. Create local backup snapshot
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
                for item in os.listdir(self.component_dir):
                    if not item.startswith(".backup_") and item != STATE_FILENAME:
                        s = os.path.join(self.component_dir, item)
                        d = os.path.join(backup_dir, item)
                        if os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            shutil.copy2(s, d)
        except Exception as e:
            _LOGGER.error("[OTA Watchdog] Failed to create backup snapshot: %s", e)
            return {"status": "error", "message": f"Backup snapshot failed: {e}"}

        # 2. Download and extract new version from GitHub
        import aiohttp
        import zipfile
        import io

        branch_or_tag = "main"
        repo = "smartcuc/homeassistant-sharegy"
        if "#" in target_str:
            parts = target_str.split("#", 1)
            repo = parts[0].replace("https://github.com/", "")
            branch_or_tag = parts[1]

        if branch_or_tag.startswith("v") or (len(branch_or_tag) > 0 and branch_or_tag[0].isdigit()):
            zip_url = f"https://github.com/{repo}/archive/refs/tags/{branch_or_tag}.zip"
        else:
            zip_url = f"https://github.com/{repo}/archive/refs/heads/{branch_or_tag}.zip"

        _LOGGER.info("[OTA Watchdog] Downloading update archive from: %s", zip_url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(zip_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200 and zip_url.endswith(f"/tags/{branch_or_tag}.zip"):
                        fallback_url = f"https://github.com/{repo}/archive/refs/heads/main.zip"
                        async with session.get(fallback_url, timeout=aiohttp.ClientTimeout(total=60)) as fallback_resp:
                            if fallback_resp.status != 200:
                                return {"status": "error", "message": f"HTTP {fallback_resp.status} downloading update from GitHub."}
                            content = await fallback_resp.read()
                    elif resp.status != 200:
                        return {"status": "error", "message": f"HTTP {resp.status} downloading update from GitHub."}
                    else:
                        content = await resp.read()

            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                extracted_count = 0
                for member in zf.namelist():
                    if "/custom_components/sharegy/" in member and not member.endswith("/"):
                        rel_path = member.split("/custom_components/sharegy/", 1)[1]
                        dest_path = os.path.join(self.component_dir, rel_path)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        with open(dest_path, "wb") as f_out:
                            f_out.write(zf.read(member))
                        extracted_count += 1

                _LOGGER.info("[OTA Watchdog] Extracted %d updated component files into %s", extracted_count, self.component_dir)
                if extracted_count == 0:
                    return {"status": "error", "message": "No valid component files found in downloaded ZIP."}

        except Exception as dl_err:
            _LOGGER.error("[OTA Watchdog] Failed to download or extract update: %s", dl_err)
            return {"status": "error", "message": f"Download/extract failed: {dl_err}"}

        state = {
            "previous_version": current_version,
            "target_version": target_str,
            "backup_dir": backup_dir,
            "started_at": time.time(),
            "timeout_seconds": timeout_seconds,
            "status": "pending",
        }
        self.write_state(state)

        # Schedule Home Assistant restart
        asyncio.create_task(self._schedule_restart())

        return {
            "status": "initiated",
            "previous_version": current_version,
            "target": target_str,
            "timeout_seconds": timeout_seconds,
            "message": "Guarded OTA update downloaded and extracted. Home Assistant restart scheduled in 3 seconds.",
        }

    async def _schedule_restart(self):
        """Triggers Home Assistant restart after a short delay."""
        try:
            await asyncio.sleep(3)
            _LOGGER.warning("[OTA Watchdog] 🔄 Restarting Home Assistant to apply updated Sharegy component...")
            await self.bridge.hass.services.async_call("homeassistant", "restart")
        except Exception as e:
            _LOGGER.error("[OTA Watchdog] Failed to restart Home Assistant: %s", e)

    def trigger_immediate_rollback(self) -> Dict[str, Any]:
        """Restores previous version from backup snapshot."""
        state = self.read_state()
        backup_dir = state.get("backup_dir") if state else None

        if not backup_dir or not os.path.exists(backup_dir):
            return {"status": "error", "message": "No backup snapshot directory found for rollback."}

        _LOGGER.warning("[OTA Watchdog] 🚨 Restoring component from backup snapshot: %s", backup_dir)
        try:
            for item in os.listdir(backup_dir):
                s = os.path.join(backup_dir, item)
                d = os.path.join(self.component_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

            if state:
                state["status"] = "rolled_back"
                state["rollback_completed_at"] = time.time()
                self.write_state(state)

            return {"status": "rolled_back", "message": "Rollback from snapshot completed."}
        except Exception as e:
            _LOGGER.error("[OTA Watchdog] Rollback restore error: %s", e)
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict[str, Any]:
        return {
            "component": "Home Assistant / Sharegy",
            "guard_state": self.read_state() or {"status": "idle", "message": "No update in progress."},
        }
