from __future__ import unicode_literals

from django.db import models
from utils.app import item_upload_to
from core.models.mixin import BaseModel, ContentStatusEnum, Currency


class ETF(BaseModel):
    STATUS_INITIALIZED = 1001
    STATUS_LISTED = 1002
    STATUS_DELISTED = 1003

    STATUS_CHOICES = [
        (STATUS_INITIALIZED, "Initialized"),
        (STATUS_LISTED, "Listed"),
        (STATUS_DELISTED, "Delisted"),
    ]

    class Meta:
        db_table = "etf"
        app_label = "core"
        ordering = ("-created",)

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50, unique=True)
    datetime = models.DateTimeField(auto_now_add=True)

    inav_symbol = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)
    currency = models.CharField(max_length=10, default=Currency.VND)
    exchange = models.CharField(max_length=50, null=False)
    type = models.CharField(max_length=50, null=True, blank=True)
    bloomberg_symbol = models.CharField(max_length=50, null=True, blank=True)
    inception_date = models.DateField(null=True, blank=True)
    reference_index = models.CharField(max_length=50, null=False, db_index=True, blank=True)
    fund_manager = models.CharField(max_length=500, null=True, blank=True)
    custodian_bank = models.CharField(max_length=500, null=True, blank=True)
    transfer_agency = models.CharField(max_length=500, null=True, blank=True)
    index_provider = models.CharField(max_length=500, null=True, blank=True)
    authorized_participants = models.CharField(max_length=500, null=True, blank=True)
    market_maker = models.CharField(max_length=500, null=True, blank=True)
    creation_unit = models.CharField(max_length=500, null=True, blank=True)
    trading_time = models.CharField(max_length=500, null=True, blank=True)
    management_fee = models.CharField(max_length=500, null=True, blank=True)
    subscription_fee = models.CharField(max_length=500, null=True, blank=True)
    redemption_fee = models.CharField(max_length=500, null=True, blank=True)
    switching_fee = models.CharField(max_length=500, null=True, blank=True)
    trading_cycle = models.CharField(max_length=500, null=True, blank=True)
    cut_off_time = models.CharField(max_length=500, null=True, blank=True)
    dividend = models.CharField(max_length=500, null=True, blank=True)
    strategy = models.TextField(null=True, blank=True)
    investment_objective = models.TextField(null=True, blank=True)

    ipo_price = models.IntegerField(default=0)
    ipo_shares = models.BigIntegerField(default=0)
    outstanding_shares = models.BigIntegerField(default=0)

    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)
    exchange_status = models.SmallIntegerField(default=STATUS_INITIALIZED, choices=STATUS_CHOICES)


class ETFFinancialReportYearly(BaseModel):
    class Meta:
        db_table = "etf_financial_report_yearly"
        app_label = "core"
        unique_together = ['symbol', 'year']

    symbol = models.CharField(max_length=50, db_index=True)
    year = models.IntegerField(default=0, null=True)
    total_assets = models.IntegerField(default=0, null=True)
    total_liabilities = models.IntegerField(default=0, null=True)
    total_listed_shares = models.IntegerField(default=0, null=True)
    eps = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    beta = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    def pe(self, price):
        if price and self.eps and self.eps != 0:
            return round(price / self.eps, 2)

        return None


class ETFHoldings(BaseModel):
    class Meta:
        db_table = "etf_holdings"
        app_label = "core"

    symbol = models.CharField(max_length=50, db_index=True)
    date = models.DateField(null=False, db_index=True)

    stock_symbol = models.CharField(max_length=50, db_index=True)
    ratio = models.DecimalField(max_digits=20, decimal_places=2)
    shares = models.DecimalField(max_digits=20, decimal_places=2)
    foreign_ownership = models.DecimalField(max_digits=20, decimal_places=2, null=True)
