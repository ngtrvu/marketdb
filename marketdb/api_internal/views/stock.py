from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from api_admin.serializers.stock import (
    StockDetailSerializer,
    StockSerializer,
)
from core.models.stocks.stock import Stock


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    pagination_class = None
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = [
        "status",
        "exchange_status",
        "exchange",
        "created",
        "modified",
        "outstanding_shares",
        "name",
        "inception_date",
    ]
    ordering_fields = "__all__"
    ordering = ("symbol",)
    search_fields = ["symbol", "name", "brand_name"]
    lookup_field = "symbol"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StockDetailSerializer
        return self.serializer_class
