#################
# market/admin.py
#################


from django.contrib import admin
from django.utils.html import format_html
from .models import SpotPrice
from market.models_tariff import HomeTariff
from market.models_price_config import ElectricityPriceConfig
from market.models_analysis import SpotPriceDaySummary

@admin.register(SpotPrice)
class SpotPriceAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "price_formatted",
        "price_eur_per_mwh",
        "source",
        "created_at",
    )
    list_filter = ("source",)
    search_fields = ("source",)
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)
    actions = ["fetch_spot_prices"]

    @admin.display(ordering="price_eur_per_kwh", description="Preis (ct/kWh)")
    def price_formatted(self, obj):
        ct = float(obj.price_eur_per_kwh * 100)
        formatted_ct = f"{ct:,.2f} ct/kWh"
        if ct < 0:
            return format_html('<span style="background: #FEE2E2; color: #DC2626; font-weight: 700; padding: 2px 8px; border-radius: 6px;">🚨 {}</span>', formatted_ct)
        elif ct < 15:
            return format_html('<span style="color: #059669; font-weight: 600;">{}</span>', formatted_ct)
        elif ct < 30:
            return format_html('<span style="color: #374151;">{}</span>', formatted_ct)
        else:
            return format_html('<span style="color: #D97706; font-weight: 700;">{}</span>', formatted_ct)

    @admin.display(description="Börsenpreis (EUR/MWh)")
    def price_eur_per_mwh(self, obj):
        mwh = obj.price_eur_per_kwh * 1000
        return f"{mwh:,.2f} €/MWh"

    @admin.action(description="📈 Spotpreise jetzt fetchen")
    def fetch_spot_prices(self, request, queryset):
        from market.tasks import fetch_spot_prices_retry
        fetch_spot_prices_retry.delay()
        self.message_user(request, "Spotpreis-Fetch wurde angestoßen!")


@admin.register(HomeTariff)
class HomeTariffAdmin(admin.ModelAdmin):

    list_display = (
        "home",
        "tariff_type",
        "valid_from",
        "static_price_eur_per_kwh",
    )

    ordering = ("-valid_from",)


@admin.register(ElectricityPriceConfig)
class ElectricityPriceConfigAdmin(admin.ModelAdmin):

    list_display = (
        "valid_from",
        "grid_fee_ct",
        "vat_percent",
    )

    ordering = ("-valid_from",)


@admin.register(SpotPriceDaySummary)
class SpotPriceDaySummaryAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "cheapest_hour",
        "cheapest_hour_price",
        "best_2h_start",
        "best_3h_start",
        "best_5h_start",
    )

    ordering = ("-date",)

    search_fields = ("date",)
