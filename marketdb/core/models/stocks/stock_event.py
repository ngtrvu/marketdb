from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class StockEvent(BaseModel):
    class Meta:
        db_table = "stock_event"
        app_label = "core"
        unique_together = ["symbol", "public_date", "name"]

    DIVIDEND_TYPE_CASH = "cash"
    DIVIDEND_TYPE_STOCK = "stock"

    DIVIDEND_TYPE_CHOICES = [
        (DIVIDEND_TYPE_CASH, "Cash"),
        (DIVIDEND_TYPE_STOCK, "Stock"),
    ]

    EVENT_TYPE_DIVIDEND = "dividend"
    EVENT_TYPE_ISSUE = "issue"

    EVENT_TYPE_CHOICES = [
        (EVENT_TYPE_DIVIDEND, "Dividend"),
        (EVENT_TYPE_ISSUE, "Issue"),
    ]

    symbol = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    public_date = models.DateField(db_index=True, null=True)

    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)

    record_date = models.DateField(db_index=True, null=True)  # Ngay DKCC
    exright_date = models.DateField(db_index=True, null=True)
    issue_date = models.DateField(db_index=True, null=True)

    value = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    ratio = models.DecimalField(max_digits=20, decimal_places=4, null=True)

    dividend_type = models.CharField(
        default=DIVIDEND_TYPE_CASH, choices=DIVIDEND_TYPE_CHOICES, max_length=50, null=True
    )

    event_type = models.CharField(
        default=EVENT_TYPE_DIVIDEND, choices=EVENT_TYPE_CHOICES, max_length=50
    )


class StockEventLog(BaseModel):
    class Meta:
        db_table = "stock_event_log"
        app_label = "core"

    DIVIDEND_TYPE_CASH = "cash"
    DIVIDEND_TYPE_STOCK = "stock"

    DIVIDEND_TYPE_CHOICES = [
        (DIVIDEND_TYPE_CASH, "Cash"),
        (DIVIDEND_TYPE_STOCK, "Stock"),
    ]

    EVENT_TYPE_DIVIDEND = "dividend"
    EVENT_TYPE_ISSUE = "issue"

    EVENT_TYPE_CHOICES = [
        (EVENT_TYPE_DIVIDEND, "Dividend"),
        (EVENT_TYPE_ISSUE, "Issue"),
    ]
    # event_id = models.CharField(max_length=100, db_index=True, unique=True)
    public_date = models.DateField(db_index=True, null=True)

    symbol = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)

    record_date = models.DateField(db_index=True, null=True)  # Ngay DKCC
    exright_date = models.DateField(db_index=True, null=True)
    issue_date = models.DateField(db_index=True, null=True)

    value = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    ratio = models.DecimalField(max_digits=20, decimal_places=4, null=True)

    dividend_type = models.CharField(
        default=DIVIDEND_TYPE_CASH, choices=DIVIDEND_TYPE_CHOICES, max_length=50, null=True
    )

    event_type = models.CharField(
        default=EVENT_TYPE_DIVIDEND, choices=EVENT_TYPE_CHOICES, max_length=50
    )


# class StockEventV2(BaseModel):
#     class Meta:
#         db_table = "stock_event_v2"
#         app_label = "core"
    
#     EVENT_TYPE_CASH_DIVIDEND = "CashDividend"
#     EVENT_TYPE_STOCK_DIVIDEND = "StockDividend"
#     EVENT_TYPE_ISSUE = "Issue"
#     EVENT_TYPE_CHOICES = [
#         (EVENT_TYPE_CASH_DIVIDEND, "Cash Dividend"),
#         (EVENT_TYPE_STOCK_DIVIDEND, "Stock Dividend"),
#         (EVENT_TYPE_ISSUE, "Issue"),
#     ]

#     symbol = models.CharField(max_length=50, db_index=True)
#     event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
#     name = models.CharField(max_length=100)
#     description = models.TextField(null=True, blank=True)

#     record_date = models.DateField(max_length=20, null=True, blank=True)  # Ngay DKCC
#     exright_date = models.DateField(max_length=20, null=True)
#     issue_date = models.DateField(max_length=20, null=True, blank=True)
#     public_date = models.DateField(max_length=20, null=True, blank=True)
    
#     value = models.DecimalField(max_digits=20, decimal_places=4, null=True)
#     ratio = models.DecimalField(max_digits=20, decimal_places=4, null=True)

#     reference_id = models.CharField(max_length=255, null=True, blank=True)
