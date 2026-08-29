##########################
# demo/services/cleanup.py
##########################

import logging
from datetime import timedelta
from django.utils import timezone
from django.db import connection
from django.contrib.auth import get_user_model

from demo.models import DemoDeviceMap
from devices.models import (
    Device,
    DeviceMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
)

logger = logging.getLogger(__name__)
User = get_user_model()
DEMO_EMAIL = "demo@sharegy.de"


def cleanup_demo_metrics(days=28):
    """
    Bereinigt veraltete Demo-Telemetriedaten (Raw Metrics & Aggregationen).
    Behandelt TimescaleDB-Komprimierungsgrenzen sicher und löscht zeitfensterbasiert.
    """
    cutoff = timezone.now() - timedelta(days=days)

    demo_ids = set()
    demo_user = User.objects.filter(email=DEMO_EMAIL).first()
    if demo_user:
        demo_ids.update(Device.objects.filter(home__user=demo_user).values_list("id", flat=True))
    demo_ids.update(DemoDeviceMap.objects.values_list("demo_device_id", flat=True))

    demo_ids = list(demo_ids)

    if not demo_ids:
        logger.info("[DemoCleanup] Keine Demo-Geräte gefunden. Überspringe Cleanup.")
        return 0


    total_deleted = 0

    # 1. TimescaleDB Decompression Limit & Raw Device Metrics Löschung
    try:
        from django.db import transaction
        with transaction.atomic():
            with connection.cursor() as cursor:
                try:
                    cursor.execute("SET LOCAL timescaledb.max_tuples_decompressed_per_dml_transaction = 0;")
                except Exception as guc_err:
                    logger.debug("[DemoCleanup] TimescaleDB GUC nicht verfügbar: %s", guc_err)

                cursor.execute(
                    """
                    DELETE FROM devices_devicemetric 
                    WHERE device_id = ANY(%s) AND timestamp < %s;
                    """,
                    [demo_ids, cutoff],
                )
                deleted = cursor.rowcount
                if deleted is not None and deleted > 0:
                    total_deleted += deleted
                    logger.info("[DemoCleanup] %d veraltete DeviceMetric-Einträge via SQL gelöscht.", deleted)
    except Exception as e:
        logger.warning("[DemoCleanup] Direktes SQL fehlgeschlagen (%s), versuche ORM-Löschung...", e)
        try:
            deleted, _ = DeviceMetric.objects.filter(
                device_id__in=demo_ids,
                timestamp__lt=cutoff,
            ).delete()
            total_deleted += deleted
            logger.info("[DemoCleanup] %d veraltete DeviceMetric-Einträge via ORM gelöscht.", deleted)
        except Exception as orm_err:
            logger.error("[DemoCleanup] Auch ORM-Löschung fehlgeschlagen: %s", orm_err)

    # 2. Aggregierte Tabellen bereinigen (1m, 5m, 15m, 1h)

    for model_cls, name in [
        (DeviceMetric1m, "1m"),
        (DeviceMetric5m, "5m"),
        (DeviceMetric15m, "15m"),
        (DeviceMetric1h, "1h"),
    ]:
        try:
            agg_deleted, _ = model_cls.objects.filter(
                device_id__in=demo_ids,
                bucket__lt=cutoff,
            ).delete()
            if agg_deleted:
                logger.info("[DemoCleanup] %d Einträge aus DeviceMetric%s gelöscht.", agg_deleted, name)
        except Exception as agg_err:
            logger.warning("[DemoCleanup] Fehler beim Bereinigen von DeviceMetric%s: %s", name, agg_err)

    return total_deleted
