##################################################
# devices/management/commands/seed_device_setup.py
##################################################

from django.core.management.base import BaseCommand
from devices.models import DeviceRole, MetricDefinition


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        roles = {
            "consumer": "Verbraucher",
            "producer": "Erzeuger",
            "battery": "Speicher",
            "grid": "Netzanschluss",
            "sensor": "Sensor",
            "both": "Beides",
        }

        for key, label in roles.items():
            DeviceRole.objects.update_or_create(
                key=key,
                defaults={"label": label}
            )

        metrics = {
            # Elektrische Größen
            "power": ("Wirkleistung", "W"),
            "active_power": ("Wirkleistung", "W"),
            "apparent_power": ("Scheinleistung", "VA"),
            "reactive_power": ("Blindleistung", "var"),
            "energy": ("Energie", "kWh"),
            "energy_import": ("Netzbezug (Zählerstand)", "kWh"),
            "energy_export": ("Einspeisung (Zählerstand)", "kWh"),
            "voltage": ("Spannung", "V"),
            "voltage_l1": ("Spannung L1", "V"),
            "voltage_l2": ("Spannung L2", "V"),
            "voltage_l3": ("Spannung L3", "V"),
            "current": ("Stromstärke", "A"),
            "current_l1": ("Strom L1", "A"),
            "current_l2": ("Strom L2", "A"),
            "current_l3": ("Strom L3", "A"),
            "frequency": ("Netzfrequenz", "Hz"),
            "power_factor": ("Leistungsfaktor (cos φ)", ""),
            # Speicher & Batterie
            "soc": ("Batterieladezustand (SoC)", "%"),
            "soh": ("Batteriegesundheit (SoH)", "%"),
            # Umwelt-, Klima- & physikalische Sensoren
            "temperature": ("Temperatur", "°C"),
            "humidity": ("Relative Luftfeuchtigkeit", "%"),
            "pressure": ("Luftdruck", "hPa"),
            "co2": ("CO2-Konzentration", "ppm"),
            "voc": ("Luftqualität (VOC)", "ppb"),
            "illuminance": ("Beleuchtungsstärke / Helligkeit", "lx"),
            "solar_radiation": ("Sonneneinstrahlung", "W/m²"),
            "wind_speed": ("Windgeschwindigkeit", "m/s"),
            # Wärme, Wasser & Durchfluss
            "flow_temperature": ("Vorlauftemperatur", "°C"),
            "return_temperature": ("Rücklauftemperatur", "°C"),
            "flow_rate": ("Durchflussrate", "l/h"),
            "heat_power": ("Wärmeleistung", "kW"),
            "percentage": ("Prozentwert", "%"),
        }

        for key, (name, unit) in metrics.items():
            MetricDefinition.objects.update_or_create(
                key=key,
                defaults={"name": name, "unit": unit}
            )