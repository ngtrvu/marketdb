from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.etfs.etf import ETF


class ETFSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = ETF
        fields = "__all__"
        singular_resource_name = "item"


class ETFDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = ETF
        fields = "__all__"
        singular_resource_name = "item"


class ETFNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETF
        fields = ["id", "name", "symbol"]


class ETFCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETF
        fields = "__all__"


class ETFUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETF
        fields = "__all__"
