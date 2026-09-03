###############################################
# devices/management/commands/mqtt_monitor.py
###############################################

from django.core.management.base import BaseCommand
from devices.models import Device
from devices.services.device_health import device_status


class Command(BaseCommand):
    help = "MQTT Monitoring / Health Check"

    def handle(self, *args, **options):

        total = 0
        offline = 0
        stale = 0
        never = 0

        devices = Device.objects.all()

        for d in devices:
            total += 1

            status = device_status(d)

            if status == "offline":
                offline += 1
            elif status == "stale":
                stale += 1
            elif status == "never_seen":
                never += 1

        self.stdout.write(f"Total devices: {total}")
        self.stdout.write(f"Offline: {offline}")
        self.stdout.write(f"Stale: {stale}")
        self.stdout.write(f"Never seen: {never}")

        if stale > 0:
            self.stdout.write("[ERROR] Some devices are stale")

        if offline > 0:
            self.stdout.write("[WARN] Some devices recently offline")

        if stale == 0 and offline == 0:
            self.stdout.write("[OK] All devices healthy")
                       