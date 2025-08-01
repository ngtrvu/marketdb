from __future__ import unicode_literals

from django.db import models
from utils.app import item_upload_to
from core.models.mixin import BaseModel, ContentStatusEnum


class Industry(BaseModel):
    class Meta:
        db_table = "industry"
        app_label = "core"
        verbose_name_plural = "industries"
        ordering = ("-created",)

    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, db_index=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)
    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)
    level = models.SmallIntegerField(null=True)
    path = models.CharField(max_length=100, null=True, blank=True)
    icb_code = models.CharField(max_length=10, null=True, blank=True)
    parent = models.ForeignKey(
        'Industry',
        related_name='industries',
        on_delete=models.PROTECT,
        null=True, blank=True,
    )
