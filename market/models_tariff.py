#########################
# market/models_tariff.py
#########################

import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from devices.models import Home


class HomeTariff(models.Model):

    TARIFF_DYNAMIC = "dynamic"
    TARIFF_STATIC = "static"

    TARIFF_CHOICES = [
        (TARIFF_DYNAMIC, "Dynamic"),
        (TARIFF_STATIC, "Static"),
    ]

    FEED_IN_STATIC = "static"
    FEED_IN_DYNAMIC = "dynamic"
    FEED_IN_NONE = "none"

    FEED_IN_CHOICES = [
        (FEED_IN_STATIC, "Feste EEG-Vergütung"),
        (FEED_IN_DYNAMIC, "Börsen-Marktwert Solar"),
        (FEED_IN_NONE, "Keine Vergütung (Nulleinspeisung)"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="tariffs",
    )

    valid_from = models.DateField()

    tariff_type = models.CharField(
        max_length=20,
        choices=TARIFF_CHOICES,
        default=TARIFF_DYNAMIC,
    )

    static_price_eur_per_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    feed_in_tariff_type = models.CharField(
        max_length=20,
        choices=FEED_IN_CHOICES,
        default=FEED_IN_STATIC,
    )

    feed_in_tariff_eur_per_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0.0820,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = ["-valid_from"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "home",
                    "valid_from",
                ],
                name="unique_home_tariff_date",
            ),
        ]

    def clean(self):

        if (
            self.tariff_type == self.TARIFF_STATIC
            and self.static_price_eur_per_kwh is None
        ):
            raise ValidationError(
                {
                    "static_price_eur_per_kwh": "Für statische Tarife muss ein Strompreis hinterlegt werden."
                }
            )

        if (
            self.tariff_type == self.TARIFF_DYNAMIC
            and self.static_price_eur_per_kwh is not None
        ):
            raise ValidationError(
                {
                    "static_price_eur_per_kwh": "Bei dynamischen Tarifen darf kein statischer Preis eingetragen werden."
                }
            )

        if (
            self.feed_in_tariff_type == self.FEED_IN_STATIC
            and self.feed_in_tariff_eur_per_kwh is None
        ):
            self.feed_in_tariff_eur_per_kwh = Decimal("0.0820")

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return f"{self.home.name} | " f"{self.tariff_type} | " f"{self.valid_from}"
