from __future__ import unicode_literals

import datetime
import uuid

from django.db import models
from core.models.mixin import BaseModel


class IndustryAnalytics(BaseModel):
    class Meta:
        db_table = "industry_analytics"
        app_label = "core"
        verbose_name_plural = "industry_analytics"
        ordering = ("-created",)
 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    industry_id = models.IntegerField(unique=True, null=False, db_index=True)
    datetime = models.DateTimeField(default=datetime.datetime.now)

    market_cap = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_1d = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_1w = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_1m = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_3m = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_6m = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_ytd = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_1y = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_3y = models.DecimalField(max_digits=50, decimal_places=0, null=True)
    market_cap_5y = models.DecimalField(max_digits=50, decimal_places=0, null=True)

    change_percentage_1d = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    pe = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    forecasted_growth = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    icb_code = models.CharField(max_length=10, unique=True, null=True)
