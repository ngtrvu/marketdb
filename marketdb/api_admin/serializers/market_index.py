from rest_framework import serializers

from core.models.market_index.market_index import MarketIndex


class MarketIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndex
        fields = "__all__"
        singular_resource_name = "item"


class MarketIndexDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndex
        fields = "__all__"
        singular_resource_name = "item"


class MarketIndexNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndex
        fields = ["id", "name", "symbol"]


class MarketIndexCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndex
        fields = "__all__"


class MarketIndexUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndex
        fields = "__all__"
