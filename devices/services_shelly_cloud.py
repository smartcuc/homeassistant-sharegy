#######################################
# devices/services_shelly_cloud.py
#######################################

import logging
import requests
from typing import Dict, Any, List, Optional
from django.utils import timezone
from devices.models import Device, DeviceConfig, CloudDeviceIntegration

logger = logging.getLogger("devices.shelly_cloud")

DEFAULT_SHELLY_CLOUD_HOST = "https://shelly-45-eu.shelly.cloud"


class ShellyCloudService:
    """
    Konnektor zur offiziellen Shelly Cloud API (REST).
    Ermöglicht 1-Klick Auto-Discovery aller im Shelly-Account registrierten Geräte
    (z.B. Shelly Pro 3EM, Plus 1PM, Shelly Plug S, Mini Gen3).
    """

    @staticmethod
    def _normalize_host(server_url: Optional[str]) -> str:
        if not server_url or not server_url.strip():
            return DEFAULT_SHELLY_CLOUD_HOST
        url = server_url.strip().rstrip("/")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        return url

    @classmethod
    def test_connection(cls, auth_key: str, server_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Prüft den Shelly Cloud Auth-Key gegen den Status-Endpunkt /device/all_status.
        """
        if not auth_key:
            return {"success": False, "error": "Auth-Key / API-Token ist erforderlich."}

        host = cls._normalize_host(server_url)
        endpoint = f"{host}/device/all_status"

        try:
            resp = requests.post(
                endpoint,
                data={"auth_key": auth_key},
                timeout=12,
            )
            if resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"Shelly Cloud Server meldete HTTP {resp.status_code}: {resp.text[:200]}",
                }

            data = resp.json()
            if not data.get("isok", False):
                return {
                    "success": False,
                    "error": data.get("errors", {}).get("error", "Ungültiger Shelly Auth-Key oder Server-URL."),
                }

            devices_dict = data.get("data", {}).get("devices", {})
            device_count = len(devices_dict)

            # Geräte extrahieren & typisieren
            discovered = []
            for dev_id, dev_data in devices_dict.items():
                status = dev_data.get("status", {})
                discovered.append({
                    "id": dev_id,
                    "name": dev_data.get("name") or dev_id,
                    "online": dev_data.get("online", False),
                    "model": dev_data.get("code") or dev_data.get("gen", "Shelly Device"),
                    "power_w": status.get("apower") or (status.get("emeters", [{}])[0].get("power") if status.get("emeters") else 0.0),
                })

            return {
                "success": True,
                "server_url": host,
                "device_count": device_count,
                "devices": discovered,
                "message": f"Verbindung erfolgreich! {device_count} Shelly-Gerät(e) gefunden.",
            }

        except requests.RequestException as e:
            logger.warning("Shelly Cloud connection error: %s", str(e))
            return {"success": False, "error": f"Verbindungsfehler zur Shelly Cloud: {str(e)}"}
        except Exception as e:
            logger.exception("Unexpected error during Shelly Cloud test")
            return {"success": False, "error": str(e)}

    @classmethod
    def import_all_devices(cls, home, auth_key: str, server_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Importiert alle Geräte aus dem Shelly Cloud Account in das angegebene Sharegy Home.
        Erstellt Device + DeviceConfig Einträge für Zähler, Steckdosen und Erzeuger.
        """
        test_res = cls.test_connection(auth_key, server_url)
        if not test_res.get("success"):
            return test_res

        host = cls._normalize_host(server_url)
        endpoint = f"{host}/device/all_status"

        try:
            resp = requests.post(endpoint, data={"auth_key": auth_key}, timeout=15)
            data = resp.json()
            devices_dict = data.get("data", {}).get("devices", {})

            created_count = 0
            updated_count = 0
            imported_devices = []

            for dev_id, dev_data in devices_dict.items():
                dev_name = dev_data.get("name") or f"Shelly {dev_id[-6:]}"
                code = (dev_data.get("code") or "").lower()
                identifier = f"shelly-{dev_id}"[:64]

                # Device erstellen oder aktualisieren
                device, created = Device.objects.get_or_create(
                    home=home,
                    identifier=identifier,
                    defaults={
                        "configured": True,
                        "active": True,
                    },
                )

                if not created:
                    device.active = True
                    device.configured = True
                    device.save(update_fields=["active", "configured"])
                    updated_count += 1
                else:
                    created_count += 1

                # DeviceConfig für Namensanzeige
                config, _ = DeviceConfig.objects.get_or_create(
                    device=device,
                    defaults={"home": home, "name": dev_name},
                )
                if config.name != dev_name:
                    config.name = dev_name
                    config.save(update_fields=["name"])

                # CloudDeviceIntegration für Polling konfigurieren
                integration, int_created = CloudDeviceIntegration.objects.get_or_create(
                    device=device,
                    defaults={
                        "profile_id": f"shelly_cloud_{code}" if code else "shelly_cloud_device",
                        "credentials": {
                            "auth_key": auth_key,
                            "server_url": host,
                            "device_id": dev_id,
                        },
                        "polling_interval_seconds": 30,
                        "is_active": True,
                        "last_status": CloudDeviceIntegration.STATUS_OK,
                    },
                )
                if not int_created:
                    integration.credentials = {
                        "auth_key": auth_key,
                        "server_url": host,
                        "device_id": dev_id,
                    }
                    integration.is_active = True
                    integration.save(update_fields=["credentials", "is_active"])

                imported_devices.append({
                    "id": device.id,
                    "name": config.name,
                    "identifier": identifier,
                    "created": created,
                })

            return {
                "success": True,
                "created_count": created_count,
                "updated_count": updated_count,
                "total_imported": len(imported_devices),
                "devices": imported_devices,
                "message": f"{created_count} neue(s) Shelly-Gerät(e) importiert, {updated_count} aktualisiert.",
            }

        except Exception as e:
            logger.exception("Error importing Shelly Cloud devices")
            return {"success": False, "error": str(e)}
