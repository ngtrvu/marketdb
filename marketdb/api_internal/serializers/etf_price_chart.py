from rest_framework import serializers

from core.models.etfs.etf_price_chart import ETFPriceChart


class ETFPriceChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETFPriceChart
        exclude = [
            "movement_1w",
            "movement_1m",
            "movement_3m",
            "movement_6m",
            "movement_1y",
            "movement_3y",
            "movement_5y",
            "movement_ytd",
            "movement_all",
        ]
