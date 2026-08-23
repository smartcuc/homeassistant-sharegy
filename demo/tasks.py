###############
# demo/tasks.py
###############

from celery import shared_task

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
    return generate_demo_telemetry()


@shared_task
def cleanup_demo():
    """
    Bereinigt veraltete Demo-Telemetriedaten (Retention-Cleanup).
    """
    return cleanup_demo_metrics()
