from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class StockPriceChart(BaseModel):
    class Meta:
        db_table = "stock_price_chart"
        app_label = "core"
        ordering = ("-created",)

    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    datetime = models.DateTimeField()

    # last closed daily volume, price, fb, fs
    reference = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    # chart movement
    movement_1w = models.JSONField(default=list, blank=True, null=True)
    movement_1m = models.JSONField(default=list, blank=True, null=True)
    movement_3m = models.JSONField(default=list, blank=True, null=True)
    movement_6m = models.JSONField(default=list, blank=True, null=True)
    movement_1y = models.JSONField(default=list, blank=True, null=True)
    movement_3y = models.JSONField(default=list, blank=True, null=True)
    movement_5y = models.JSONField(default=list, blank=True, null=True)
    movement_ytd = models.JSONField(default=list, blank=True, null=True)
