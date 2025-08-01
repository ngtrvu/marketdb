from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.stocks.stock import Stock


class StockSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Stock
        fields = "__all__"
        singular_resource_name = "item"


class StockDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Stock
        fields = "__all__"
        singular_resource_name = "item"


class StockNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["id", "name", "symbol"]


class StockCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class StockUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"
