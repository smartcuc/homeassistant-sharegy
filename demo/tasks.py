###############
# demo/tasks.py
###############

from celery import shared_task

from demo.services.data_generator import (
    generate_demo_telemetry,
    setup_demo_household,
)
from demo.services.cleanup import (
    cleanup_demo_metrics,
)


@shared_task
def sync_demo_metrics():
    """
    Erzeugt dynamische, physikalisch realistische Telemetriedaten
    für das unabhängige Demo Smart Home.
    """
    return generate_demo_telemetry()


@shared_task
def sync_demo_devices():
    """
    Stellt sicher, dass das Demo Smart Home mit allen Geräten existiert.
    """
    setup_demo_household()
    return {"status": "ok"}


@shared_task
def sync_demo_configs():
    return {"status": "ok"}


@shared_task
def cleanup_demo():
    return cleanup_demo_metrics()
