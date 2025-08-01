from __future__ import unicode_literals

import uuid

from django.db import models
from xpider.models.mixin import BaseModel


class NewsPost(BaseModel):

    class Meta:
        db_table = "xpider_post"
        app_label = "xpider"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doc_id = models.CharField(max_length=255, db_index=True, unique=True)
    slug = models.CharField(max_length=500, db_index=True)
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    published = models.DateTimeField(db_index=True, null=True)
    description = models.TextField(null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    thumbnail_url = models.TextField(null=True, blank=True)

    publisher_name = models.CharField(max_length=100, null=True, blank=True)
    publisher_website = models.CharField(max_length=500, null=True, blank=True)
    
    category = models.CharField(max_length=50, default="cryptocurrency", db_index=True)
    language = models.CharField(max_length=50, default="vi", db_index=True)

    symbols = models.JSONField(default=list)
    topics = models.JSONField(default=list)
    tags = models.JSONField(default=list)

    is_relevant = models.BooleanField(db_index=True, default=True)
    is_recommend = models.BooleanField(db_index=True, default=False)
    relevant_score = models.FloatField(null=True)


class NewsTopic(BaseModel):

    class Meta:
        db_table = "xpider_news_topic"
        app_label = "xpider"
        unique_together = ['doc_id', 'topic_token']

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doc_id = models.CharField(max_length=255, db_index=True)
    topic_token = models.CharField(max_length=500, db_index=True)


class Topic(BaseModel):

    class Meta:
        db_table = "xpider_topic"
        app_label = "xpider"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic_token = models.CharField(max_length=500, db_index=True)
    name = models.CharField(max_length=500)
    slug = models.CharField(max_length=500, db_index=True)
    type = models.CharField(max_length=50, db_index=True)
    description = models.TextField(null=True, blank=True)
    meta_data = models.JSONField(default=dict)


class NewsTrending(BaseModel):

    class Meta:
        db_table = "xpider_news_trending"
        app_label = "xpider"

    doc_id = models.CharField(max_length=255, db_index=True, unique=True)
    meta_data = models.JSONField(default=dict)


class NewsIndustry(BaseModel):

    class Meta:
        db_table = "xpider_news_industry"
        app_label = "xpider"
        unique_together = ['doc_id', 'icb_code']

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doc_id = models.CharField(max_length=255, db_index=True)
    icb_code = models.CharField(max_length=500, db_index=True)
    is_correct = models.BooleanField(db_index=True, default=True)
