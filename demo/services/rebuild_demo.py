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
    Baut das autonome Demo Smart Home vollständig neu auf (keine Nutzerdaten-Kopie mehr)
    und erzeugt initiale Telemetriedaten.
    """
    home = setup_demo_household()
    telemetry = generate_demo_telemetry()

    return {
        "status": "ok",
        "home_id": str(home.id),
        "home_name": home.name,
        "devices": home.devices.count(),
        "telemetry": telemetry,
    }
