from rest_framework import serializers

from core.models.market_index.market_index import MarketIndex


class MarketIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndex
        fields = ['symbol', 'name', 'description']
