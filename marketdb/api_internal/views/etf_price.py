from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.models.etfs.etf_price_chart import ETFPriceChart
from api.views.etfs.etf_price import ETFPriceDetailView
from api_internal.serializers.etf_price_chart import ETFPriceChartSerializer


class InternalETFPriceDetailView(ETFPriceDetailView):
    pass


class InternalETFPriceChartView(ReadOnlyModelViewSet):
    queryset = ETFPriceChart.objects.all()
    serializer_class = ETFPriceChartSerializer
    pagination_class = None
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = [
        "symbol",
        "datetime",
    ]
    ordering_fields = "__all__"
    ordering = ("symbol",)
    search_fields = ["symbol", "name"]
    lookup_field = "symbol"
