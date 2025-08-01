from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class CryptoPriceRealtime(BaseModel):
    class Meta:
        db_table = "crypto_price_realtime"
        app_label = "core"

    symbol = models.CharField(max_length=50, unique=True, db_index=True)
    datetime = models.DateTimeField()

    # value (in VND)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    high = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    low = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    all_time_high = models.DecimalField(max_digits=20, decimal_places=0, default=0)

    # market cap
    market_cap = models.DecimalField(max_digits=51, decimal_places=0)

    # 24 realtime volume (total trading value in VND as crypto annotation)
    volume = models.DecimalField(max_digits=20, decimal_places=0, default=0)

    # 24h realtime change
    change_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    change_value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    market_cap_change_value = models.DecimalField(max_digits=51, decimal_places=0, null=True)
    market_cap_change_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True)
