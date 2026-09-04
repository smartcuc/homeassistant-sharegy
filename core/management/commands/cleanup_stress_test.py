##################################################
# core/management/commands/cleanup_stress_test.py
##################################################

import time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction

from devices.models import (
    Home,
    Device,
    DeviceMetric,
    DeviceLatestMetric,
    DeviceMetric1h,
    DeviceConfig,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Cleanup all stress test users, homes, devices, and metrics completely"

    def add_arguments(self, parser):
        parser.add_argument(
            "--pattern",
            type=str,
            default="stress_user_",
            help="Prefix pattern for users to delete (default: stress_user_)",
        )

    def handle(self, *args, **options):
        pattern = options["pattern"]
        start_time = time.time()

        self.stdout.write(
            self.style.NOTICE(f"[CLEANUP] Starting cleanup for users matching '{pattern}*'...")
        )

        users_qs = User.objects.filter(email__startswith=pattern) | User.objects.filter(username__startswith=pattern)
        user_count = users_qs.count()

        if user_count == 0:
            self.stdout.write(self.style.WARNING("No stress test users found to clean up."))
            return

        user_ids = list(users_qs.values_list("id", flat=True))
        home_ids = list(Home.objects.filter(user_id__in=user_ids).values_list("id", flat=True))
        device_ids = list(Device.objects.filter(home_id__in=home_ids).values_list("id", flat=True))

        self.stdout.write(
            f"Found: {user_count} users, {len(home_ids)} homes, {len(device_ids)} devices."
        )

        with transaction.atomic():
            # 1. Delete metrics in bulk
            dm1h_deleted, _ = DeviceMetric1h.objects.filter(device_id__in=device_ids).delete()
            dlm_deleted, _ = DeviceLatestMetric.objects.filter(device_id__in=device_ids).delete()
            dm_deleted, _ = DeviceMetric.objects.filter(device_id__in=device_ids).delete()

            # 2. Delete configs & devices
            cfg_deleted, _ = DeviceConfig.objects.filter(device_id__in=device_ids).delete()
            dev_deleted, _ = Device.objects.filter(id__in=device_ids).delete()

            # 3. Delete homes & users
            homes_deleted, _ = Home.objects.filter(id__in=home_ids).delete()
            users_deleted, _ = users_qs.delete()

        # Clear Redis cache keys
        try:
            for u_id in user_ids:
                cache.delete(f"ws_update_{u_id}")
            for d_id in device_ids:
                cache.delete_many([
                    f"dedup:{d_id}:power",
                    f"dedup:{d_id}:energy",
                ])
        except Exception:
            pass

        elapsed = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"[OK] Cleaned up successfully in {elapsed:.2f}s:\n"
                f"   - Users deleted: {users_deleted}\n"
                f"   - Homes deleted: {homes_deleted}\n"
                f"   - Devices deleted: {dev_deleted}\n"
                f"   - DeviceConfigs deleted: {cfg_deleted}\n"
                f"   - LatestMetrics deleted: {dlm_deleted}\n"
                f"   - DeviceMetrics deleted: {dm_deleted}\n"
                f"   - 1h Metrics deleted: {dm1h_deleted}"
            )
        )
