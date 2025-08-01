from rest_framework import serializers

from core.models.cryptos.crypto_price_realtime import CryptoPriceRealtime

DATE_RANGES = ["24h", "1w", "1m", "1y"]


class CryptoPriceRealtimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CryptoPriceRealtime
        fields = ['symbol', 'name', 'photo', 'market_cap']


class CryptoPriceRealtimeSerializer(serializers.ModelSerializer):
    date_range = serializers.SerializerMethodField()
    date_ranges = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField()

    class Meta:
        model = CryptoPriceRealtime
        fields = [
            'symbol', 'symbol', 'datetime', 'price', 'high', 'low', 'all_time_high', 'market_cap', 'volume',
            'change_percentage', 'change_value', 'market_cap_change_value', 'market_cap_change_percentage',
            'date_range', 'date_ranges', 'prices'
        ]

    def get_date_ranges(self, obj):
        return DATE_RANGES

    def get_date_range(self, obj):
        date_range = self.context.get('date_range', '24h')
        date_range = date_range.lower()

        if date_range in DATE_RANGES:
            return date_range
        return '24h'

    def get_prices(self, obj):
        return []
