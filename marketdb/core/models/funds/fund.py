from __future__ import unicode_literals

from django.db import models
from utils.app import item_upload_to
from core.models.mixin import BaseModel, ContentStatusEnum, Currency


class MutualFund(BaseModel):
    class Meta:
        db_table = "fund"
        app_label = "core"

    symbol = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)
    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)
    currency = models.CharField(max_length=10, default=Currency.VND)
    is_on_stag = models.BooleanField(default=False)

    inception_date = models.DateField(null=True, blank=True)
    conversion_date = models.DateField(null=True, blank=True)
    fund_manager = models.CharField(max_length=500, null=True, blank=True)
    custodian_bank = models.CharField(max_length=500, null=True, blank=True)
    transfer_agency = models.CharField(max_length=500, null=True, blank=True)

    distributors = models.CharField(max_length=500, null=True, blank=True)
    management_fee = models.CharField(max_length=500, null=True, blank=True)
    subscription_fee = models.CharField(max_length=500, null=True, blank=True)
    redemption_fee = models.CharField(max_length=500, null=True, blank=True)
    switching_fee = models.CharField(max_length=500, null=True, blank=True)
    trading_cycle = models.CharField(max_length=500, null=True, blank=True)
    cut_off_time = models.CharField(max_length=500, null=True, blank=True)
    dividend = models.CharField(max_length=500, null=True, blank=True)
    strategy = models.TextField(null=True, blank=True)
    investment_objective = models.TextField(null=True, blank=True)


class MutualFundHoldings(BaseModel):
    class Meta:
        db_table = "fund_holdings"
        app_label = "core"

    symbol = models.CharField(max_length=50, db_index=True)
    date = models.DateField(null=False, db_index=True)

    stock_symbol = models.CharField(max_length=50, db_index=True)
    ratio = models.DecimalField(max_digits=20, decimal_places=2)
