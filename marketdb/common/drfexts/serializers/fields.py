from django.conf import settings
from rest_framework import serializers


def image_handler_url(url: str):
    media_url = settings.MEDIA_URL if url and str(url).startswith('/') else settings.MEDIA_URL
    if url:
        url = url.lstrip("/")
        return f"{media_url}/cdn-cgi/image/width=350,quality=75,format=auto/{url}"
    return


def video_handler_url(url: str):
    media_url = settings.MEDIA_URL if url and str(url).startswith('/') else settings.MEDIA_URL
    if url:
        url = url.lstrip("/")
        return f"{media_url}/{url}"
    return


class ImageHandlerSerializer(serializers.ImageField):
    """
    Image field are serialized to resize image by img handler
    """
    def __init__(self, alias=None, **kwargs):
        super(ImageHandlerSerializer, self).__init__(**kwargs)

    def to_representation(self, value):
        if value:
            return image_handler_url(url=str(value))
        return ""


class VideoHandlerSerializer(serializers.ImageField):
    """
    Image field are serialized to resize image by img handler
    """
    def __init__(self, alias=None, **kwargs):
        super(VideoHandlerSerializer, self).__init__(**kwargs)

    def to_representation(self, value):
        if value:
            return video_handler_url(url=str(value))
        return ""


class ExternalImageSerializer(serializers.ImageField):
    """
    Image field are serialized to resize image by img handler
    """
    def __init__(self, host_alias: str, host_url: str, **kwargs):
        self.host_url: str = host_url
        self.host_alias: str = host_alias

        super(ExternalImageSerializer, self).__init__(**kwargs)

    def to_representation(self, value):
        if value:
            return str(value).replace(f"//{self.host_alias}", self.host_url)
        return ""


class TimestampField(serializers.Field):
    def to_representation(self, value):
        return value.timestamp()
