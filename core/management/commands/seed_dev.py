##########################################
# core/management/commands/seed_dev.py
##########################################

from datetime import datetime, timezone as tz
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection, transaction

from core.models import Meter, IntervalReading

User = get_user_model()


class Command(BaseCommand):
    help = "Seed dev data (user, meter, readings) and run rollup + balance."


    def handle(self, *args, **options):

        with transaction.atomic():

            # ✅ 1) USER
            user, created = User.objects.get_or_create(
                username="testuser",
                defaults={
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "is_active": True,
                    "is_verified": False,
                },
            )

            if created:
                user.set_password("testpass123")
                user.save()

            # ✅ 2) METER (Owner Pattern korrekt)
            meter, _ = Meter.objects.get_or_create(
                serial_number="TEST-METER-001",
                defaults={
                    "owner_user": user,
                    "owner_membership": None,  # ✅ FIX
                    "tenant": None,
                    "meter_type": "electricity",
                    "manufacturer": "TestVendor",
                },
            )

            # ✅ 3) INTERVAL DATA
            start = datetime(2026, 1, 1, 10, 0, tzinfo=tz.utc)
            end = datetime(2026, 1, 1, 10, 15, tzinfo=tz.utc)

            IntervalReading.objects.update_or_create(
                meter=meter,
                ts_start=start,
                obis_code="1.8.0",
                defaults={
                    "tenant": None,
                    "ts_end": end,
                    "value": Decimal("1.5"),  # ✅ FIX
                    "unit": "kWh",
                    "source": "seed",
                },
            )

            IntervalReading.objects.update_or_create(
                meter=meter,
                ts_start=start,
                obis_code="2.8.0",
                defaults={
                    "tenant": None,
                    "ts_end": end,
                    "value": Decimal("0.8"),  # ✅ FIX
                    "unit": "kWh",
                    "source": "seed",
                },
            )

        # ✅ 4) CORE PIPELINE TRIGGERN
        with connection.cursor() as cur:
            cur.execute("SELECT rollup_15min();")              # ✅ FIX
            cur.execute("SELECT process_dirty_balance();")     # ✅ FIX

        self.stdout.write(
            self.style.SUCCESS(
                "[OK] Seed done "
                "(User=testuser/testpass123, Meter=TEST-METER-001, "
                "Pipeline executed)"
            )
        )
        