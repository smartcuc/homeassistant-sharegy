#############################################
# devices/management/commands/rebuild_mqtt.py
#############################################

from django.core.management.base import BaseCommand
from devices.models import Home
from devices.tasks import provision_home


class Command(BaseCommand):
    help = "Rebuild only missing MQTT users"

    def handle(self, *args, **options):
        homes = Home.objects.filter(mqtt_provisioned=False)

        self.stdout.write(f"Provisioning {homes.count()} missing homes...")

        for home in homes:
            self.stdout.write(f"-> provisioning {home.mqtt_username}")
            provision_home.delay(home.id)

        self.stdout.write("[OK] Done")

