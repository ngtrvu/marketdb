from rest_framework import serializers

from xpider.models.news import NewsPost


class NewsPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsPost
        fields = [
            'uuid', 'title', 'slug', 'description', 'url', 'thumbnail_url', 'publisher_name',
            'published', 'created', 'symbols', 'language', 'category',
        ]


class NewsPostDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsPost
        fields = '__all__'


class NewsTopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsPost
        fields = [
            'uuid', 'title', 'slug', 'description', 'url', 'thumbnail_url', 'publisher_name',
            'published', 'created', 'symbols', 'language', 'category',
        ]