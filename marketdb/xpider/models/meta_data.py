from __future__ import unicode_literals

import uuid

from django.db import models
from xpider.models.mixin import BaseModel


class Category(BaseModel):

    class Meta:
        db_table = "xpider_category"
        app_label = "xpider"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500)
    slug = models.CharField(max_length=500, db_index=True)
    description = models.TextField(null=True, blank=True)


class Entity(BaseModel):

    class Meta:
        db_table = "xpider_entity"
        app_label = "xpider"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500)
    slug = models.CharField(max_length=500, db_index=True)
    type = models.CharField(max_length=50, db_index=True)
    description = models.TextField(null=True, blank=True)
    meta_data = models.JSONField(default=dict)


class NERLabel(BaseModel):
    class Meta:
        db_table = "xpider_ner_label"
        app_label = "xpider"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_uuid = models.UUIDField()
    name = models.CharField(max_length=500)
    label = models.CharField(max_length=50, db_index=True)
    start = models.IntegerField(null=True)
    end = models.IntegerField(null=True)
    text = models.TextField(null=True, blank=True)  # input text
