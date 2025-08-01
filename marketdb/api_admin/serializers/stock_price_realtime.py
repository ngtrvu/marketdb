from rest_framework import serializers

from core.models.stocks.stock_price_realtime import StockPriceRealtime


class StockPriceRealtimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockPriceRealtime
        fields = '__all__'
        singular_resource_name = 'item'
