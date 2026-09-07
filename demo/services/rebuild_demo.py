###############################
# demo/services/rebuild_demo.py
###############################

import logging
from demo.services.data_generator import (
    setup_demo_household,
    generate_demo_telemetry,
)

logger = logging.getLogger(__name__)


def rebuild_demo_environment():
    """
    Baut das autonome Demo Smart Home (HEMS) sowie die Energy Sharing Community Demos
    (Admin & Mieterstrom) vollständig neu auf und erzeugt initiale Telemetriedaten.
    """
    home = setup_demo_household()
    telemetry = generate_demo_telemetry()

    sharing_data = {}
    try:
        from accounts.services_demo_sharing import seed_sharing_demo_environment
        sharing_data = seed_sharing_demo_environment()
    except Exception as e:
        logger.warning("Sharing-Demo-Initialisierung fehlgeschlagen: %s", e)

    return {
        "status": "ok",
        "home_id": str(home.id),
        "home_name": home.name,
        "devices": home.devices.count(),
        "telemetry": telemetry,
        "sharing_admin": sharing_data.get("admin_user", {}).email if hasattr(sharing_data.get("admin_user"), "email") else "sharing-admin@sharegy.de",
        "sharing_member": sharing_data.get("member_user", {}).email if hasattr(sharing_data.get("member_user"), "email") else "sharing-user@sharegy.de",
    }
