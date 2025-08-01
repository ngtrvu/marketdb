from __future__ import unicode_literals

from django.db import models
from core.models.mixin import BaseModel


class MarketStatusEnum:
    OPEN = 1001
    CLOSE = 1002


class MarketCalendar(BaseModel):

    class Meta:
        db_table = "market_calendar"
        app_label = "core"
        ordering = ("-created",)

    date = models.DateField(db_index=True, unique=True)
    status = models.SmallIntegerField(default=MarketStatusEnum.OPEN)
    description = models.TextField(null=True, blank=True)
