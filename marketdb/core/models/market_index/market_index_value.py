from __future__ import unicode_literals

from django.db import models

from core.models.mixin import BaseModel, ContentStatusEnum


class MarketIndexValue(BaseModel):
    class Meta:
        db_table = "market_index_value"
        app_label = "core"
        unique_together = ['symbol']
        ordering = ("-created",)

    symbol = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    datetime = models.DateTimeField(null=False)

    exchange = models.CharField(max_length=50, db_index=True, null=True, blank=True)
    open = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    value = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    total_value = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_volume = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    ordering = models.IntegerField(db_index=True, default=0)
    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)
