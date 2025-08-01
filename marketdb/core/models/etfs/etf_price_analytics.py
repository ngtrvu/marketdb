from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class ETFPriceAnalytics(BaseModel):
    class Meta:
        db_table = "etf_price_analytics"
        app_label = "core"
        verbose_name_plural = "etf_price_analytics"
        ordering = ("-created",)

    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    datetime = models.DateTimeField()

    # last closed daily volume, price, fb, fs
    reference = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    price_1d = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    volume_1d = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    total_trading_value = models.DecimalField(
        max_digits=20, decimal_places=2, default=0
    )

    # daily batch calculation
    price_1w = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price_1m = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price_3m = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price_6m = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price_1y = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price_3y = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price_5y = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price_ytd = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    price_inception_date = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )

    # change percentage - update realtime
    change_percentage_1w = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    change_percentage_1m = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    change_percentage_3m = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    change_percentage_6m = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    change_percentage_1y = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    change_percentage_3y = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    change_percentage_5y = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    change_percentage_ytd = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )
    change_percentage_inception_date = models.DecimalField(
        max_digits=20, decimal_places=2, blank=True, null=True
    )

    volume_1w = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, blank=True, null=True
    )
    volume_1m = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, blank=True, null=True
    )
    volume_3m = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, blank=True, null=True
    )
    volume_6m = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, blank=True, null=True
    )
    volume_1y = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, blank=True, null=True
    )
    volume_3y = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, blank=True, null=True
    )
    volume_5y = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, blank=True, null=True
    )
    volume_ytd = models.DecimalField(
        max_digits=20, decimal_places=2, default=0, blank=True, null=True
    )
