from rest_framework import serializers

from core.models.market.market_calendar import MarketCalendar


class MarketCalendarSerializer(serializers.ModelSerializer):

    class Meta:
        model = MarketCalendar
        fields = '__all__'
        singular_resource_name = 'item'


class MarketCalendarDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = MarketCalendar
        fields = ['date', 'status', 'description']
        singular_resource_name = 'item'


class MarketCalendarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketCalendar
        fields = '__all__'


class MarketCalendarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketCalendar
        fields = '__all__'
