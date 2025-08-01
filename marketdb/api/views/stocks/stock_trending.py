from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.query import QuerySet
from django.db.models import Q

from core.models.mixin import AssetType
from core.models.stocks.stock import Stock
from core.models.stocks.stock_price_realtime import StockPriceRealtime
from api.serializers.stock_price_realtime import (
    StockPriceRealtimeSerializer,
)


class TrendingStockView(GenericViewSet, ListModelMixin):
    lookup_field = "symbol"
    serializer_class = StockPriceRealtimeSerializer
    queryset = StockPriceRealtime.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_fields = ["exchange"]
    ordering_fields = ["total_trading_value", "volume"]
    ordering = ("-total_trading_value",)

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        queryset = queryset.filter(volume__gt=0)
        queryset = queryset.filter(Q(type=AssetType.STOCK) | Q(type=AssetType.ETF))

        stock_table_name = Stock.objects.model._meta.db_table
        stock_price_table_name = StockPriceRealtime.objects.model._meta.db_table
        queryset = queryset.extra(
            tables=[stock_table_name],
            where=[
                "{0}.symbol={1}.symbol".format(stock_price_table_name, stock_table_name)
            ],
            select={
                "stock_photo": f"{stock_table_name}.photo",
                "stock_name": f"{stock_table_name}.name",
            },
        )
        return queryset
