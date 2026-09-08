##################
# market/models.py
##################

import uuid
from django.db import models
# market/models.py

from .models_analysis import SpotPriceDaySummary

class SpotPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    timestamp = models.DateTimeField()

    price_eur_per_kwh = models.DecimalField(max_digits=10, decimal_places=6)

    source = models.CharField(max_length=50, default="energy-charts")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["timestamp", "source"], name="uniq_price_ts_source"
            )
        ]
        indexes = [models.Index(fields=["timestamp"])]

    def __str__(self):
        return f"{self.timestamp} → {self.price_eur_per_kwh} €/kWh"

    @property
    def price_ct_kwh(self):
        if self.price_eur_per_kwh is not None:
            return float(self.price_eur_per_kwh * 100)
        return 0.0
