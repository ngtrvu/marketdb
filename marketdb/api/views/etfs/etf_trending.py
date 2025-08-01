from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.query import QuerySet
from django.db.models import Q

from core.models.mixin import AssetType
from core.models.etfs.etf import ETF
from core.models.etfs.etf_price_chart import ETFPriceChart
from core.models.stocks.stock_price_realtime import StockPriceRealtime
from api.serializers.etf_price_realtime import ETFPriceRealtimeSerializer
from api.serializers.etf_price_chart import ETFPriceChartSerializer


class ETFTrendingView(GenericViewSet, ListModelMixin):
    lookup_field = "symbol"
    serializer_class = ETFPriceChartSerializer
    queryset = ETFPriceChart.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_fields = []
    ordering_fields = ["total_trading_value", "volume"]
    ordering = ("-total_trading_value",)

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        queryset = queryset.order_by("-total_trading_value")

        # etf_price_table_name = StockPriceRealtime.objects.model._meta.db_table
        etf_info = ETF.objects.model._meta.db_table
        etf_price_chart = ETFPriceChart.objects.model._meta.db_table

        queryset = queryset.extra(
            tables=[etf_info, etf_price_chart],
            where=[
                # "{0}.symbol={1}.symbol".format(etf_price_table_name, etf_table_name),
                "{0}.symbol={1}.symbol".format(etf_info, etf_price_chart),
            ],
            select={
                "photo": f"{etf_info}.photo",
                "name": f"{etf_info}.name",
            },
        )
        return queryset
