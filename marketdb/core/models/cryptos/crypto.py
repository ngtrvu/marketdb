from __future__ import unicode_literals

from django.db import models
from utils.app import item_upload_to
from core.models.mixin import BaseModel, ContentStatusEnum, Currency


class Crypto(BaseModel):
    class Meta:
        db_table = "crypto"
        app_label = "core"

    name = models.CharField(max_length=500)
    symbol = models.CharField(max_length=10, unique=True)
    coingecko_id = models.CharField(max_length=500, unique=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)
    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)
    currency = models.CharField(max_length=10, default=Currency.VND)

    market_cap_rank = models.IntegerField(default=99999, db_index=True)
    market_cap = models.DecimalField(max_digits=51, decimal_places=0, null=True)
    fully_diluted_valuation = models.DecimalField(max_digits=51, decimal_places=0, null=True)
    circulating_supply = models.BigIntegerField(null=True)
    total_supply = models.BigIntegerField(null=True)
    max_supply = models.BigIntegerField(null=True)
