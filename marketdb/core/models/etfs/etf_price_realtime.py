from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel, AssetType


class ETFPriceRealtime(BaseModel):
    """ETFPriceRealtime contains realtime prices from exchange, including all ETFs
    """

    class Meta:
        db_table = "etf_price_realtime"
        app_label = "core"
        ordering = ("-created",)

    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    datetime = models.DateTimeField()
    exchange = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    type = models.CharField(max_length=50, default=AssetType.ETF, db_index=True)

    price = models.DecimalField(max_digits=20, decimal_places=2)
    volume = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    fb_volume = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    fs_volume = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    foreign_room = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_trading_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    open = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    reference = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    ceiling = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    floor = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    change_percentage_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    market_cap = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    outstanding_shares = models.DecimalField(max_digits=20, decimal_places=0, null=True)

    ordering = models.IntegerField(db_index=True, blank=True, null=True)
