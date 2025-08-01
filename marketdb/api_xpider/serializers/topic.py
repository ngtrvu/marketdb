from rest_framework import serializers

from xpider.models.news import Topic


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = [
            'uuid', 'topic_token', 'name', 'slug', 'type'
        ]


class TopicDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = '__all__'
