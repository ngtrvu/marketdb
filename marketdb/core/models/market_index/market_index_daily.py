from __future__ import unicode_literals

from django.db import models

from core.models.mixin import BaseModel


class MarketIndexDaily(BaseModel):
    class Meta:
        db_table = "market_index_daily"
        app_label = "core"
        unique_together = ["symbol", "date"]
        ordering = ("symbol",)

    symbol = models.CharField(max_length=50, db_index=True)
    date = models.DateField(null=False)
    datetime = models.DateTimeField(null=False)

    open = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    total_volume = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    total_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
