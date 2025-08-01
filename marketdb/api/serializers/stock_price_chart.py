from rest_framework import serializers

from common.drfexts.serializers.fields import TimestampField
from core.models.stocks.stock_price_chart import StockPriceChart


class StockPriceChartDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPriceChart
        fields = ["id", "symbol", "datetime"]


class StockPriceChartMovementSerializer(serializers.ModelSerializer):
    symbol = serializers.StringRelatedField()
    date_range = serializers.StringRelatedField()
    datetime = serializers.StringRelatedField()
    price = serializers.DecimalField(max_digits=10, decimal_places=4)
    change_value = serializers.DecimalField(max_digits=10, decimal_places=4)
    change_percentage = serializers.DecimalField(max_digits=10, decimal_places=4)
    prices = serializers.ListField()

    class Meta:
        model = StockPriceChart
        fields = (
            "symbol",
            "date_range",
            "datetime",
            "price",
            "change_value",
            "change_percentage",
            "prices",
        )


class OHLCItemSerializer(serializers.Serializer):
    o = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)  # open price
    h = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)  # high price
    l = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)  # low price
    c = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)  # close price
    v = serializers.DecimalField(max_digits=10, decimal_places=0, required=False)  # volume
    t = TimestampField(required=True)  # timestamp in integer


class SimplePriceItemSerializer(serializers.Serializer):
    c = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)  # close price
    v = serializers.DecimalField(max_digits=10, decimal_places=0, required=False)  # volume
    t = TimestampField(required=True)  # timestamp in integer
