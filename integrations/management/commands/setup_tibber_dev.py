######################################################
# integrations/management/commands/setup_tibber_dev.py
######################################################

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Meter
import uuid
import os


User = get_user_model()


class Command(BaseCommand):
    help = "Setup minimal Tibber dev environment"

    def handle(self, *args, **kwargs):
        self.stdout.write("[INFO] Setting up Tibber dev environment...")

        # --- Token aus ENV ---
        tibber_token = os.getenv("TIBBER_TOKEN")
        tibber_home_id = os.getenv("TIBBER_HOME_ID")

        if not tibber_token or not tibber_home_id:
            self.stdout.write(self.style.ERROR(
                "[ERROR] Missing TIBBER_TOKEN or TIBBER_HOME_ID in .env"
            ))
            return

        # --- User holen oder erstellen ---
        user, created = User.objects.get_or_create(
            username="dev_tibber",
            defaults={
                "email": "dev@example.com",
            }
        )

        user.tibber_token = tibber_token
        user.tibber_home_id = tibber_home_id
        user.set_password("devpassword")
        user.save()

        if created:
            self.stdout.write("[OK] User created")
        else:
            self.stdout.write("[OK] User updated")

        # --- Meter erstellen ---
        meter, created = Meter.objects.get_or_create(
            tibber_home_id=tibber_home_id,
            defaults={
                "id": uuid.uuid4(),
                "meter_type": "electricity",
                "manufacturer": "Tibber",
                "owner_user": user,
                "integration_type": "tibber",
            }
        )

        if created:
            self.stdout.write("[OK] Meter created")
        else:
            # sicherstellen, dass Integration korrekt gesetzt ist
            meter.integration_type = "tibber"
            meter.owner_user = user
            meter.save()
            self.stdout.write("[OK] Meter updated")

        self.stdout.write(self.style.SUCCESS(
            "[OK] Tibber dev setup complete!"
        ))

