from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.stocks.stock_event import StockEvent, StockEventLog


class StockEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockEvent
        fields = "__all__"
        singular_resource_name = "item"


class StockEventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockEvent
        fields = "__all__"
        singular_resource_name = "item"


class StockEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockEvent
        fields = "__all__"


class StockEventUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockEvent
        fields = "__all__"


class StockEventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockEventLog
        fields = "__all__"
        singular_resource_name = "item"


class StockEventLogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockEventLog
        fields = "__all__"
        singular_resource_name = "item"