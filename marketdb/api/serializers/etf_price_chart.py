from rest_framework import serializers
from common.drfexts.serializers.fields import ImageHandlerSerializer

from core.models.etfs.etf_price_chart import ETFPriceChart


class NestedETFPriceChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETFPriceChart
        fields = [
            "id",
            "symbol",
            "datetime",
            "price_1y",
            "price_ytd",
            "change_percentage_1y",
            "change_percentage_ytd",
        ]


class ETFPriceChartSerializer(serializers.ModelSerializer):
    change_value = serializers.SerializerMethodField()
    change_percentage = serializers.SerializerMethodField()
    name = serializers.CharField(read_only=True)
    photo = ImageHandlerSerializer()

    class Meta:
        model = ETFPriceChart
        fields = [
            "id",
            "symbol",
            "name",
            "photo",
            "datetime",
            "total_trading_value",
            "reference",
            "price",
            "change_value",
            "change_percentage",
            "price_1d",
            "price_1w",
            "price_1y",
            "price_ytd",
            "change_percentage_1w",
            "change_percentage_1y",
            "change_percentage_ytd",
        ]

    def get_change_value(self, obj):
        if not obj.reference or not obj.price:
            return None

        return obj.price - obj.reference

    def get_change_percentage(self, obj):
        if not obj.reference or not obj.price:
            return None

        return ((obj.price - obj.reference) / obj.reference) * 100


class ETFPriceChartDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETFPriceChart
        fields = "__all__"


class ETFPriceChartMovementSerializer(serializers.ModelSerializer):
    symbol = serializers.StringRelatedField()
    date_range = serializers.StringRelatedField()
    datetime = serializers.StringRelatedField()
    price = serializers.DecimalField(max_digits=10, decimal_places=4)
    change_value = serializers.DecimalField(max_digits=10, decimal_places=4)
    change_percentage = serializers.DecimalField(max_digits=10, decimal_places=4)
    prices = serializers.ListField()

    class Meta:
        model = ETFPriceChart
        fields = (
            "symbol",
            "date_range",
            "datetime",
            "price",
            "change_value",
            "change_percentage",
            "prices",
        )
