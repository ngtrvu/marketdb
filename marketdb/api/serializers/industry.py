from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.industries.industry import Industry


class IndustrySerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Industry
        fields = ["id", "name", "slug", "photo"]


class IndustryDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Industry
        fields = "__all__"


class NestedIndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ["id", "name", "icb_code"]
