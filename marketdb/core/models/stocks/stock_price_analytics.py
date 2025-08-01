from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class StockPriceAnalytics(BaseModel):
    class Meta:
        db_table = "stock_price_analytics"
        app_label = "core"
        verbose_name_plural = "stock_price_analytics"
        ordering = ("-created",)

    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    date = models.DateField(null=True)
    datetime = models.DateTimeField()

    # last closed daily volume, price, fb, fs
    reference = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    volume_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    fb_volume_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    fs_volume_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    price_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    price_inception_date = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    # change percentage - update realtime
    change_percentage_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_inception_date = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    volume_1w = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    volume_1m = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    volume_3m = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    volume_6m = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    volume_1y = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    volume_3y = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    volume_5y = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
