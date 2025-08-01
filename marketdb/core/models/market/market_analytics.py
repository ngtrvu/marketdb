from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class FearGreedIndexDaily(BaseModel):
    class Meta:
        db_table = "fear_greed_index_daily"
        app_label = "core"
        ordering = ("-created",)

    date = models.DateField(unique=True, db_index=True)
    datetime = models.DateTimeField(null=False)
    score = models.DecimalField(max_digits=20, decimal_places=2)

    market_index = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    market_index_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    market_index_diff = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    volatility = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    volatility_sma = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    rsi = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    momentum = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    momentum_diff = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    price_breadth = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    price_breadth_diff = models.DecimalField(max_digits=20, decimal_places=10, null=True)
    price_strength = models.DecimalField(max_digits=20, decimal_places=10, null=True)
