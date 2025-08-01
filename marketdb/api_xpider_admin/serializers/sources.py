from rest_framework import serializers

from xpider.models.sources import LandingPage, Publisher


class PageSerializer(serializers.ModelSerializer):

    class Meta:
        model = LandingPage
        fields = '__all__'
        singular_resource_name = 'item'


class PublisherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publisher
        fields = '__all__'
        singular_resource_name = 'item'