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

    # 1. TimescaleDB Decompression Limit für diese DB-Session aufheben (0 = unbegrenzt)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET timescaledb.max_tuples_decompressed_per_dml_transaction = 0;")
    except Exception as e:
        logger.debug("[DemoCleanup] TimescaleDB GUC nicht verfügbar oder nicht erforderlich: %s", e)

    # 2. Raw Device Metrics löschen
    try:
        deleted, _ = DeviceMetric.objects.filter(
            device_id__in=demo_ids,
            timestamp__lt=cutoff,
        ).delete()
        total_deleted += deleted
        logger.info("[DemoCleanup] %d veraltete DeviceMetric-Einträge gelöscht (älter als %d Tage).", deleted, days)
    except Exception as e:
        logger.error("[DemoCleanup] Standard-Delete fehlgeschlagen, versuche SQL-Fallback mit SET LOCAL: %s", e)
        # Fallback: Direktes SQL mit gesetztem LOCAL GUC
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SET LOCAL timescaledb.max_tuples_decompressed_per_dml_transaction = 0;
                    DELETE FROM devices_devicemetric 
                    WHERE device_id = ANY(%s) AND timestamp < %s;
                    """,
                    [demo_ids, cutoff],
                )
                deleted = cursor.rowcount
                total_deleted += deleted
                logger.info("[DemoCleanup] SQL-Fallback erfolgreich: %d Einträge gelöscht.", deleted)
        except Exception as fb_err:
            logger.error("[DemoCleanup] Auch SQL-Fallback fehlgeschlagen: %s", fb_err)
            raise fb_err

    # 3. Aggregierte Tabellen bereinigen (1m, 5m, 15m, 1h)
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
