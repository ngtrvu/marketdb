from __future__ import unicode_literals

from django.db import models

from xpider.models.mixin import BaseModel


class Industry(BaseModel):

    class Meta:
        db_table = "xpider_industry"
        app_label = "xpider"

    name = models.CharField(max_length=255)
    icb_code = models.CharField(max_length=500, db_index=True)
    level = models.SmallIntegerField(null=True)
    keywords = models.JSONField(default=list)
