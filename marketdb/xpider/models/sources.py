from __future__ import unicode_literals

from django.db import models

from xpider.models.mixin import BaseModel


class Publisher(BaseModel):

    class Meta:
        db_table = "xpider_publisher"
        app_label = "xpider"

    title = models.CharField(max_length=255)
    url = models.CharField(max_length=500)
    slug = models.CharField(max_length=500, db_index=True)
    extra_data = models.JSONField(default=dict)


class LandingPage(BaseModel):

    class Meta:
        db_table = "xpider_publisher_pages"
        app_label = "xpider"

    title = models.CharField(max_length=255)
    url = models.CharField(max_length=500)
    category = models.CharField(max_length=50, db_index=True)
    language = models.CharField(max_length=10, default="vi")
    extra_data = models.JSONField(default=dict)
