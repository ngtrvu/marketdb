from rest_framework import serializers


class ETFOrderStatsSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=4)
    volume = serializers.DecimalField(max_digits=10, decimal_places=0)
