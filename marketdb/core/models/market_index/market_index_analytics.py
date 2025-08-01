from __future__ import unicode_literals
import datetime

from django.db import models
from django.utils.timezone import now
from core.models.mixin import BaseModel

class MarketIndexAnalytics(BaseModel):
    class Meta:
        db_table = "market_index_analytics"
        app_label = "core"
        ordering = ("-created",)

    symbol = models.CharField(max_length=50, unique=True)

    # change percentage - update realtime
    close = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    datetime = models.DateTimeField(default=now)

    close_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    close_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    change_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    change_percentage_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)
