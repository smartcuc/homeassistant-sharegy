from django.core.management.base import BaseCommand
from devices.models import DeviceMetric, DeviceLatestMetric, MetricDefinition


class Command(BaseCommand):
    help = "Löscht historische daily_* Messwert-Kanäle aus DeviceMetric und DeviceLatestMetric"

    def handle(self, *args, **options):
        keys = [
            "daily_charge_kwh",
            "daily_discharge_kwh",
            "daily_feed_in_kwh",
            "daily_generation_kwh",
            "daily_import_kwh",
        ]
        
        # 1. DeviceLatestMetric bereinigen
        deleted_latest, _ = DeviceLatestMetric.objects.filter(metric_key__in=keys).delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted_latest} Einträge aus DeviceLatestMetric gelöscht."))

        # 2. DeviceMetric (Timescale / DB) bereinigen
        deleted_metrics, _ = DeviceMetric.objects.filter(metric_key__in=keys).delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted_metrics} Einträge aus DeviceMetric gelöscht."))

        # 3. MetricDefinition bereinigen, falls vorhanden
        deleted_defs, _ = MetricDefinition.objects.filter(key__in=keys).delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted_defs} Einträge aus MetricDefinition gelöscht."))
