###############
# demo/tasks.py
###############

from celery import shared_task

import logging

logger = logging.getLogger(__name__)

from demo.services.data_generator import (
    generate_demo_telemetry,
)
from demo.services.cleanup import (
    cleanup_demo_metrics,
)


@shared_task
def sync_demo_metrics():
    """
    Erzeugt kontinuierlich dynamische, physikalisch realistische Telemetriedaten
    für das autonome Demo Smart Home.
    """
    try:
        return generate_demo_telemetry()
    except Exception as e:
        logger.error("[CeleryTask:sync_demo_metrics] Fehler bei Demo-Generierung: %s", e)
        return 0


@shared_task
def cleanup_demo():
    """
    Bereinigt veraltete Demo-Telemetriedaten (Retention-Cleanup).
    """
    try:
        return cleanup_demo_metrics()
    except Exception as e:
        logger.error("[CeleryTask:cleanup_demo] Fehler beim Demo-Cleanup: %s", e)
        return 0

