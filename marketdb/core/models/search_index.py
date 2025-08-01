from __future__ import unicode_literals

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from core.models.mixin import AssetType


class SearchIndex(models.Model):
    class Meta:
        db_table = "search_index"
        app_label = "core"
        indexes = [GinIndex(fields=["search_vector"])]

    symbol = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=200, null=True, blank=True)
    photo = models.CharField(max_length=1000, null=True, blank=True)
    keywords = models.JSONField(default=list)
    type = models.CharField(max_length=50, db_index=True, default=AssetType.STOCK)

    search_vector = SearchVectorField(editable=False, null=True)
