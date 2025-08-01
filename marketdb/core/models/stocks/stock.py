from __future__ import unicode_literals

from django.db import models
from utils.app import item_upload_to
from core.models.mixin import BaseModel, ContentStatusEnum, Currency


class Stock(BaseModel):
    STATUS_INITIALIZED = 1001
    STATUS_LISTED = 1002
    STATUS_DELISTED = 1003

    STATUS_CHOICES = [
        (STATUS_INITIALIZED, "Initialized"),
        (STATUS_LISTED, "Listed"),
        (STATUS_DELISTED, "Delisted"),
    ]

    class Meta:
        db_table = "stock"
        app_label = "core"

    symbol = models.CharField(primary_key=True, max_length=50)
    datetime = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200, null=True, blank=True)
    brand_name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)
    currency = models.CharField(max_length=10, default=Currency.VND)
    exchange = models.CharField(max_length=50)
    inception_date = models.CharField(max_length=500, null=True, blank=True)

    industry = models.ForeignKey(
        "Industry",
        related_name="industry_stocks",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    super_sector = models.ForeignKey(
        "Industry",
        related_name="super_sector_stocks",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    sector = models.ForeignKey(
        "Industry",
        related_name="sector_stocks",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    sub_sector = models.ForeignKey(
        "Industry",
        related_name="sub_sector_stocks",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    ipo_price = models.IntegerField(default=0)
    ipo_shares = models.BigIntegerField(default=0)
    outstanding_shares = models.BigIntegerField(default=0)

    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)
    exchange_status = models.SmallIntegerField(
        default=STATUS_INITIALIZED, choices=STATUS_CHOICES
    )
