from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class MutualFundNavIndex(BaseModel):
    class Meta:
        db_table = "fund_nav"
        app_label = "core"

    fund = models.ForeignKey("MutualFund", on_delete=models.PROTECT, null=True)
    symbol = models.CharField(max_length=10, unique=True, db_index=True)
    date = models.DateField(null=True)
    datetime = models.DateTimeField(null=True)
    nav = models.DecimalField(max_digits=20, decimal_places=2)
    total_nav = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    # analytic data
    annualized_return_percentage = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )

    # number of year data compute return
    annualized_return_n_year = models.IntegerField(null=True)
    maximum_drawdown_percentage = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )

    nav_1w = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_1m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_3m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_6m = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_1y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_3y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_5y = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_ytd = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    nav_inception_date = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    # change percentage - update realtime
    change_percentage_1w = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )
    change_percentage_1m = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )
    change_percentage_3m = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )
    change_percentage_6m = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )
    change_percentage_1y = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )
    change_percentage_3y = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )
    change_percentage_5y = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )
    change_percentage_ytd = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )
    change_percentage_inception_date = models.DecimalField(
        max_digits=20, decimal_places=2, null=True
    )


class MutualFundNavDaily(BaseModel):
    class Meta:
        db_table = "fund_nav_daily"
        app_label = "core"
        unique_together = ["symbol", "date"]

    symbol = models.CharField(max_length=50, db_index=True)
    date = models.DateField(null=False, db_index=True)
    datetime = models.DateTimeField(null=False, db_index=True)
    nav = models.DecimalField(max_digits=20, decimal_places=2)
