from rest_framework import serializers

from core.models.stocks.stock_analytics import StockFA


class StockFASerializer(serializers.ModelSerializer):

    class Meta:
        model = StockFA
        fields = '__all__'
        singular_resource_name = 'item'
