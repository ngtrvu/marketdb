from __future__ import unicode_literals

from django.db import models

from utils.app import item_upload_to
from core.models.mixin import BaseModel, ContentStatusEnum


class ProductTypeEnum:
    STOCK = 'stock'
    ETF = 'etf'
    MUTUAL_FUND = 'mutual_fund'
    CRYPTO = 'crypto'
    BANK = 'bank'


class CollectionContentTypeEnum:
    DESKTOP = 'desktop'
    APP = 'app'


class Collection(BaseModel):
    """
    Investing Ideas
    """
    class Meta:
        db_table = "collection"
        app_label = "core"

    PRODUCT_TYPE = (
        (ProductTypeEnum.STOCK, 'Stock'),
        (ProductTypeEnum.ETF, 'ETF'),
        (ProductTypeEnum.MUTUAL_FUND, 'Mutual Fund'),
        (ProductTypeEnum.CRYPTO, 'Crypto'),
        (ProductTypeEnum.BANK, 'Bank'),
    )

    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)
    excerpt = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0)
    limit = models.IntegerField(default=12)
    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)
    product_type = models.CharField(max_length=50, default=ProductTypeEnum.STOCK)

    content_type = models.CharField(max_length=50, default=CollectionContentTypeEnum.DESKTOP)

    field_params = models.JSONField(default=list)
    filter_params = models.JSONField(default=list)
    sort_params = models.JSONField(default=list)

    group = models.ForeignKey(
        'CollectionGroup', related_name='group_collection', on_delete=models.SET_NULL, null=True, blank=True,
    )


class CollectionGroup(BaseModel):
    class Meta:
        db_table = "collection_group"
        app_label = "core"

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)
    order = models.IntegerField(default=0)
    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)


class MetricDataTypeEnum:
    CURRENCY = 'currency'
    NUMBER = 'number'
    CHANGE_PERCENTAGE = 'change_percentage'
    STRING = 'string'


class Metric(BaseModel):
    class Meta:
        db_table = "metric"
        app_label = "core"
        unique_together = ['name', 'product_type']

    name = models.CharField(max_length=255, db_index=True)
    label = models.CharField(max_length=255)
    group = models.CharField(max_length=255, db_index=True)  # For admin acp
    product_type = models.CharField(max_length=50)
    source_model = models.CharField(max_length=100)
    source_field = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50)


class WatchlistCollection(BaseModel):
    """
    Watchlist suggestion
    """
    class Meta:
        db_table = "watchlist_collection"
        app_label = "core"

    PRODUCT_TYPE = (
        (ProductTypeEnum.STOCK, 'Stock'),
        (ProductTypeEnum.ETF, 'ETF'),
        (ProductTypeEnum.MUTUAL_FUND, 'Mutual Fund'),
        (ProductTypeEnum.CRYPTO, 'Crypto'),
        (ProductTypeEnum.BANK, 'Bank'),
    )

    title = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(upload_to=item_upload_to, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0)
    limit = models.IntegerField(default=12)
    status = models.SmallIntegerField(default=ContentStatusEnum.DRAFT)
    product_type = models.CharField(max_length=50, default=ProductTypeEnum.STOCK)

    field_params = models.JSONField(default=list)
    filter_params = models.JSONField(default=list)
    sort_params = models.JSONField(default=list)
