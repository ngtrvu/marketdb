from datetime import datetime

import pytz
from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.stocks.stock_price_realtime import StockPriceRealtime


DATE_RANGES = ["1d", "1w", "1m", "3m", "1y", "5y", "all", "ytd"]
HISTORICAL_DATE_RANGES = ["1w", "1m", "3m", "1y", "5y", "all", "ytd"]


class ETFPriceRealtimeDetailSerializer(serializers.ModelSerializer):
    change_percentage = serializers.SerializerMethodField()
    change_value = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField()
    date_ranges = serializers.SerializerMethodField()
    date_range = serializers.SerializerMethodField()

    class Meta:
        model = StockPriceRealtime  # TODO: change to ETFPriceChart
        fields = [
            "id",
            "symbol",
            "datetime",
            "price",
            "volume",
            "fb_volume",
            "fs_volume",
            "foreign_room",
            "open",
            "high",
            "low",
            "close",
            "reference",
            "floor",
            "ceiling",
            "total_trading_value",
            "change_percentage",
            "change_value",
            "prices",
            "date_range",
            "date_ranges",
            "exchange",
            "type",
        ]

    def get_change_percentage(self, obj):
        return self.context.get("change_percentage")

    def get_change_value(self, obj):
        return self.context.get("change_value")

    def get_prices(self, obj):
        return self.context.get("prices", [])

    def get_date_ranges(self, obj):
        return DATE_RANGES

    def get_date_range(self, obj):
        return self.context.get("date_range")


class ETFPriceRealtimeSerializer(serializers.ModelSerializer):
    change_percentage = serializers.SerializerMethodField()
    change_value = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    stock_name = serializers.CharField(read_only=True)
    stock_photo = ImageHandlerSerializer()
    price_1y = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    change_percentage_1y = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    price_ytd = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    change_percentage_ytd = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = StockPriceRealtime
        fields = [
            "id",
            "symbol",
            "type",
            "datetime",
            "price",
            "change_percentage",
            "change_value",
            "volume",
            "total_trading_value",
            "exchange",
            "type",
            "stock_name",
            "stock_photo",
            "price_1y",
            "change_percentage_1y",
            "price_ytd",
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

    def get_stock_name(self, obj):
        return obj.stock_name

    def get_type(self, obj):
        if obj.type and isinstance(obj.type, str):
            return obj.type.lower()
        return ""
