from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.industries.industry import Industry


class IndustrySerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Industry
        fields = "__all__"
        singular_resource_name = "item"


class IndustryDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Industry
        fields = "__all__"
        singular_resource_name = "item"


class IndustryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ["id", "name", "slug"]


class IndustryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = "__all__"


class IndustryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = "__all__"
