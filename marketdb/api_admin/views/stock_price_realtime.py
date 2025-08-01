from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.stock_price_realtime import StockPriceRealtimeSerializer
from core.models.stocks.stock_price_realtime import StockPriceRealtime


class StockPriceRealtimeViewSet(viewsets.ModelViewSet):
    queryset = StockPriceRealtime.objects.all()
    serializer_class = StockPriceRealtimeSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = {
        "symbol": ["exact", "in"],
        "type": ["exact"],
        "exchange": ["exact"],
    }
    ordering_fields = "__all__"
    ordering = ("-created",)
    search_fields = ["symbol"]
    authentication_classes = [GoogleAuthentication]
