"""
Command to synchronize EPEX Spot and SMARD electricity market prices.
Usage:
    python manage.py sync_market_prices [--source=all|energy-charts|smard]
"""

from django.core.management.base import BaseCommand
from market.tasks import fetch_spot_prices, fetch_spot_prices_smard
from market.tasks_analysis import compute_daily_spot_summary


class Command(BaseCommand):
    help = "Fetches latest EPEX Spot day-ahead and intraday power market prices"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default="all",
            choices=["all", "energy-charts", "smard"],
            help="Data source to query",
        )

    def handle(self, *args, **options):
        source = options["source"]
        self.stdout.write(f"Starting market price sync (source: {source})...")

        if source in ["all", "energy-charts"]:
            res_ec = fetch_spot_prices()
            self.stdout.write(f"Energy-Charts sync result: {res_ec}")

        if source in ["all", "smard"]:
            res_smard = fetch_spot_prices_smard()
            self.stdout.write(f"SMARD sync result: {res_smard}")

        summary = compute_daily_spot_summary()
        self.stdout.write(f"Market daily summary updated: {summary}")
        self.stdout.write(self.style.SUCCESS("Market price synchronization completed successfully."))
