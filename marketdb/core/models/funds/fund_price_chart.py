from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class MutualFundPriceChart(BaseModel):
    class Meta:
        db_table = "fund_nav_chart"
        app_label = "core"

    fund = models.ForeignKey('MutualFund', on_delete=models.PROTECT, null=True)
    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    date = models.DateField(null=True)
    datetime = models.DateTimeField()

    nav_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    change_value_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_value_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_value_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_value_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_value_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_value_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_value_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_value_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    change_percentage_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    change_percentage_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)
