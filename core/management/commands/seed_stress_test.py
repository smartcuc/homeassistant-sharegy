##################################################
# core/management/commands/seed_stress_test.py
##################################################

import json
import os
import sys
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from devices.models import (
    Home,
    Floor,
    Room,
    DeviceRole,
    MetricDefinition,
    Device,
    DeviceConfig,
    DeviceLatestMetric,
)
from energy.ems.models_signal_type import EMSSignalType
from producer.models import GeneratorType

User = get_user_model()


DEVICE_TEMPLATES = [
    # (identifier_suffix, name, role_key, signal_key, gen_type_key, floor_name, room_name, initial_w)
    ("grid", "Netzuebergabepunkt / Smart Meter", "grid", "grid_power", None, "Keller", "Technikraum", 350.0),
    ("pv", "Dach-Photovoltaik 10 kWp", "producer", "pv_power", "pv", "Dach", "Technikraum", 2800.0),
    ("battery", "Heimspeicher 10 kWh", "storage", "battery_power", None, "Keller", "Technikraum", -500.0),
    ("heatpump", "Waermepumpe Heizung & WW", "consumer", "load_power", None, "Keller", "Technikraum", 1200.0),
    ("wallbox", "Wallbox 11 kW (Garage)", "consumer", "load_power", None, "EG", "Garage", 0.0),
    ("washer", "Waschmaschine", "consumer", "load_power", None, "Keller", "HWR", 45.0),
    ("dryer", "Waschetrockner", "consumer", "load_power", None, "Keller", "HWR", 0.0),
    ("dishwasher", "Geschirrspueler", "consumer", "load_power", None, "EG", "Kueche", 15.0),
    ("oven", "Backofen / Herd", "consumer", "load_power", None, "EG", "Kueche", 0.0),
    ("fridge", "Kuehlschrank", "consumer", "load_power", None, "EG", "Kueche", 65.0),
    ("freezer", "Gefrierschrank", "consumer", "load_power", None, "Keller", "HWR", 55.0),
    ("tv_living", "Smart TV & Soundbar", "consumer", "load_power", None, "EG", "Wohnzimmer", 110.0),
    ("pc_office", "Home Office Workstation", "consumer", "load_power", None, "OG", "Buero", 180.0),
    ("ac_living", "Klimaanlage Wohnzimmer", "consumer", "load_power", None, "EG", "Wohnzimmer", 0.0),
    ("ac_bedroom", "Klimaanlage Schlafzimmer", "consumer", "load_power", None, "OG", "Buero", 0.0),
    ("pump_garden", "Gartenpumpe Bewaesserung", "consumer", "load_power", None, "EG", "Garten", 0.0),
    ("ventilation", "Wohnraum lueftung (KWL)", "consumer", "load_power", None, "Keller", "Technikraum", 35.0),
    ("plug_kitchen", "Kaffeemaschine & Wasserkocher", "consumer", "load_power", None, "EG", "Kueche", 80.0),
    ("plug_living", "Stehlampe & Router", "consumer", "load_power", None, "EG", "Wohnzimmer", 40.0),
    ("pv_balcony", "Balkonkraftwerk 800 W", "producer", "pv_power", "pv", "OG", "Buero", 450.0),
]


class Command(BaseCommand):
    help = "Seed N stress test users with M devices each and export JWT tokens for load generator"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=200,
            help="Number of users to create (default: 200)",
        )
        parser.add_argument(
            "--devices-per-user",
            type=int,
            default=20,
            help="Number of devices per user (default: 20)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="StressPass2026!",
            help="Password for stress test users",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="stress_test_tokens.json",
            help="Output JSON file for generated user credentials & tokens",
        )

    def handle(self, *args, **options):
        num_users = options["users"]
        devs_per_user = min(options["devices_per_user"], len(DEVICE_TEMPLATES))
        password = options["password"]
        output_file = options["output"]

        start_time = time.time()
        self.stdout.write(
            self.style.NOTICE(
                f"[START] Seeding Stress Test: {num_users} users x {devs_per_user} devices "
                f"(= {num_users * devs_per_user} total devices)..."
            )
        )

        # 1. Ensure master metadata exists
        floors = {
            name: Floor.objects.get_or_create(name=name)[0]
            for name in ["EG", "OG", "Keller", "Dach"]
        }
        rooms = {
            name: Room.objects.get_or_create(name=name)[0]
            for name in ["Wohnzimmer", "Kueche", "HWR", "Buero", "Technikraum", "Garage", "Garten"]
        }

        roles = {
            key: DeviceRole.objects.get_or_create(key=key, defaults={"label": key.capitalize()})[0]
            for key in ["grid", "producer", "storage", "consumer"]
        }

        metric_def, _ = MetricDefinition.objects.get_or_create(
            key="power",
            defaults={"name": "Wirkleistung", "unit": "W"}
        )

        signal_types = {
            key: EMSSignalType.objects.get_or_create(key=key, defaults={"label": key, "active": True})[0]
            for key in ["grid_power", "pv_power", "battery_power", "load_power"]
        }

        pv_gen_type, _ = GeneratorType.objects.get_or_create(
            key="pv",
            defaults={"name": "Photovoltaik", "icon": "PV", "active": True}
        )

        now = timezone.now()
        tokens_export = []

        # Batch creation loop
        for u_idx in range(1, num_users + 1):
            username = f"stress_user_{u_idx:03d}"
            email = f"stress_user_{u_idx:03d}@test.sharegy.de"

            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "username": username,
                        "first_name": f"StressUser",
                        "last_name": f"#{u_idx:03d}",
                        "is_active": True,
                    }
                )
                user.set_password(password)
                if hasattr(user, "is_verified"):
                    user.is_verified = True
                user.save()

                # Create Home
                home, _ = Home.objects.get_or_create(
                    user=user,
                    defaults={
                        "name": f"Stress Home {u_idx:03d}",
                        "timezone": "Europe/Berlin",
                        "postal_code": "10115",
                        "city": "Berlin",
                        "latitude": 52.5200,
                        "longitude": 13.4050,
                    }
                )

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                user_devices_info = []

                # Create Devices
                for d_idx in range(devs_per_user):
                    tpl = DEVICE_TEMPLATES[d_idx]
                    ident = f"stress_{u_idx:03d}_{tpl[0]}"
                    dev_name = f"{tpl[1]} (U{u_idx:03d})"
                    role = roles[tpl[2]]
                    signal_type = signal_types[tpl[3]]
                    gen_type = pv_gen_type if tpl[4] == "pv" else None
                    floor = floors[tpl[5]]
                    room = rooms[tpl[6]]
                    init_w = tpl[7]

                    dev, _ = Device.objects.get_or_create(
                        home=home,
                        identifier=ident,
                        defaults={
                            "configured": True,
                            "active": True,
                        }
                    )

                    DeviceConfig.objects.update_or_create(
                        device=dev,
                        defaults={
                            "home": home,
                            "name": dev_name,
                            "role": role,
                            "generator_type": gen_type,
                            "metric_definition": metric_def,
                            "energy_signal_type": signal_type,
                            "floor": floor,
                            "room": room,
                        }
                    )

                    DeviceLatestMetric.objects.update_or_create(
                        device=dev,
                        metric_key="power",
                        defaults={
                            "value": init_w,
                            "unit": "W",
                            "timestamp": now,
                        }
                    )

                    user_devices_info.append({
                        "id": str(dev.id),
                        "identifier": ident,
                        "name": dev_name,
                        "role": tpl[2],
                        "signal": tpl[3],
                        "base_power": init_w,
                    })

                tokens_export.append({
                    "user_id": str(user.id),
                    "email": email,
                    "username": username,
                    "access_token": access_token,
                    "home_id": str(home.id),
                    "devices": user_devices_info,
                })

            if u_idx % 20 == 0 or u_idx == num_users:
                self.stdout.write(f"  -> Seeded {u_idx}/{num_users} users ({u_idx * devs_per_user} devices)...")

        # Save tokens to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "created_at": now.isoformat(),
                "num_users": num_users,
                "num_devices_per_user": devs_per_user,
                "total_devices": num_users * devs_per_user,
                "users": tokens_export,
            }, f, indent=2)

        elapsed = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f"[OK] Successfully seeded {num_users} users & {num_users * devs_per_user} devices in {elapsed:.2f}s!\n"
                f"[INFO] Tokens exported to: {output_file}"
            )
        )
