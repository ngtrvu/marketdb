from __future__ import unicode_literals

from django.db import models

from core.models.mixin import BaseModel
from utils.app import item_upload_to


class Bank(BaseModel):
    class Meta:
        db_table = "bank"
        app_label = "core"

    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, db_index=True)
    symbol = models.CharField(max_length=255, db_index=True)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)

    savings_on_demand = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_1m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_3m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_6m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_9m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_12m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_13m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_18m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_24m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    savings_36m = models.DecimalField(decimal_places=4, max_digits=20, null=True)

    online_savings_on_demand = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_1m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_3m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_6m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_9m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_12m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_13m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_18m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_24m = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    online_savings_36m = models.DecimalField(decimal_places=4, max_digits=20, null=True)

    market_cap = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    non_performing_loan_ratio = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    loan_to_deposit_ratio = models.DecimalField(decimal_places=4, max_digits=20, null=True)
    capital_adequacy_ratio = models.DecimalField(decimal_places=4, max_digits=20, null=True)
