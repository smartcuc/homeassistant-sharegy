"""
Command to trigger the central weather and PV production forecast pipeline.
Usage:
    python manage.py run_forecasts
"""

from django.core.management.base import BaseCommand
from forecast.tasks import update_all_forecasts


class Command(BaseCommand):
    help = "Executes the central multi-tenant weather and PV solar forecast calculation"

    def handle(self, *args, **options):
        self.stdout.write("Starting central forecast pipeline execution...")
        result = update_all_forecasts()
        self.stdout.write(f"Forecast pipeline completed with result: {result}")
        self.stdout.write(self.style.SUCCESS("Forecast run finished successfully."))
