#
# ore/management/commands/seed_demo.py
#

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.utils.timezone import now

from core.models import Meter, IntervalReading

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo energy data (meters + interval data + pipeline)"


    def handle(self, *args, **options):

        with transaction.atomic():

            user, created = User.objects.get_or_create(
                username="testuser",
                defaults={
                    "email": "test@sharegy.local",
                    "is_active": True,
                },
            )
            if created:
                user.set_password("testpass123")
                user.save()

            # ✅ Consumption Meter
            consumption_meter, _ = Meter.objects.get_or_create(
                serial_number="CONS-001",
                defaults={
                    "owner_user": user,
                    "owner_membership": None,
                    "tenant": None,
                    "meter_type": "consumption",
                    "manufacturer": "Demo",
                },
            )

            # ✅ Production Meter (PV)
            production_meter, _ = Meter.objects.get_or_create(
                serial_number="PV-001",
                defaults={
                    "owner_user": user,
                    "owner_membership": None,
                    "tenant": None,
                    "meter_type": "production",
                    "manufacturer": "Demo",
                },
            )

            # ✅ aktuelle Zeit → realistischer
            start = now().replace(second=0, microsecond=0)
            end = start + timedelta(minutes=15)

            # ✅ Consumption
            IntervalReading.objects.update_or_create(
                meter=consumption_meter,
                ts_start=start,
                obis_code="1.8.0",
                defaults={
                    "tenant": None,
                    "ts_end": end,
                    "value": Decimal("2.4"),
                    "unit": "kWh",
                    "source": "seed",
                },
            )

            # ✅ Production
            IntervalReading.objects.update_or_create(
                meter=production_meter,
                ts_start=start,
                obis_code="2.8.0",
                defaults={
                    "tenant": None,
                    "ts_end": end,
                    "value": Decimal("1.6"),
                    "unit": "kWh",
                    "source": "seed",
                },
            )

        # ✅ Pipeline triggern
        with connection.cursor() as cur:
            cur.execute("SELECT rollup_15min();")
            cur.execute("SELECT process_dirty_balance();")

        self.stdout.write(
            self.style.SUCCESS(
                "[OK] Demo data created (consumption + production + pipeline)"
            )
        )
        