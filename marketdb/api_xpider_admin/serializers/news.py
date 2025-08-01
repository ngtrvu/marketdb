from rest_framework import serializers

from xpider.models.news import NewsPost


class NewsPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsPost
        fields = '__all__'
        singular_resource_name = 'item'
