import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from billing.models import Coupon, EMSSubscription

class Command(BaseCommand):
    help = "Initialisiert Standard-Gutscheine (z. B. BETA100 für Betatester)"

    def handle(self, *args, **options):
        coupons = [
            {
                "code": "BETA100",
                "description": "100% Beta-Tester Rabatt: 3 Monate Sharegy Pro kostenlos",
                "discount_type": Coupon.TYPE_FREE_MONTHS,
                "discount_value": 100.00,
                "free_plan": EMSSubscription.PLAN_PRO_MONTHLY,
                "duration_months": 3,
                "max_redemptions": 500,
                "is_active": True,
            },
            {
                "code": "SUNNY2026",
                "description": "Frühlings-Aktion: 20% Rabatt auf alle Jahrestarife",
                "discount_type": Coupon.TYPE_PERCENT,
                "discount_value": 20.00,
                "free_plan": EMSSubscription.PLAN_PRO_YEARLY,
                "duration_months": 12,
                "max_redemptions": 1000,
                "is_active": True,
            },
            {
                "code": "TESTPRO",
                "description": "Entwickler- & VIP-Gutschein: 1 Monat Pro gratis",
                "discount_type": Coupon.TYPE_FREE_MONTHS,
                "discount_value": 100.00,
                "free_plan": EMSSubscription.PLAN_PRO_MONTHLY,
                "duration_months": 1,
                "max_redemptions": 100,
                "is_active": True,
            },
        ]

        for cdata in coupons:
            coupon, created = Coupon.objects.update_or_create(
                code=cdata["code"],
                defaults=cdata,
            )
            status_str = "erstellt" if created else "aktualisiert"
            self.stdout.write(self.style.SUCCESS(f"Gutschein '{coupon.code}' {status_str}!"))
