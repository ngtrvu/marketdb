from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.etfs.etf import ETF


class ETFSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = ETF
        fields = ["symbol", "name", "photo", "exchange"]


class ETFDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = ETF
        fields = "__all__"


class ETFNestedSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = ETF
        fields = ["symbol", "name", "photo", "exchange"]
