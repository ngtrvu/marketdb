from __future__ import unicode_literals

from django.db import models

from core.models.mixin import BaseModel


class MarketIndex(BaseModel):

    class Meta:
        db_table = "market_index"
        app_label = "core"
        ordering = ("-created",)

    symbol = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    stocks = models.ManyToManyField(
        "Stock",
        through="MarketIndexStock",
        through_fields=("market_index", "stock"),
    )


class MarketIndexStock(BaseModel):

    class Meta:
        db_table = "market_index_stock"
        app_label = "core"
        ordering = ("-created",)
        unique_together = ("stock", "market_index")

    stock = models.ForeignKey("Stock", on_delete=models.CASCADE)
    market_index = models.ForeignKey("MarketIndex", on_delete=models.CASCADE)
