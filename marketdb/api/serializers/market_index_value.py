from datetime import datetime

import pytz
from rest_framework import serializers

from core.models.market_index.market_index_value import MarketIndexValue
from core.models.market_index.market_index_daily import MarketIndexDaily


class MarketIndexValueSerializer(serializers.ModelSerializer):
    change_percentage = serializers.SerializerMethodField()
    change_value = serializers.SerializerMethodField()

    class Meta:
        model = MarketIndexValue
        fields = [
            "symbol",
            "datetime",
            "exchange",
            "open",
            "value",
            "change_percentage",
            "change_value",
            "total_volume",
            "total_value",
        ]

    def get_change_percentage(self, obj):
        return ((obj.value - obj.open) / obj.open) * 100

    def get_change_value(self, obj):
        return obj.value - obj.open


class MarketIndexDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndexDaily
        fields = ["date", "open", "high", "low", "close", "total_volume", "total_value"]
