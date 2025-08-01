from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from api_admin.serializers.market_index import (
    MarketIndexDetailSerializer,
    MarketIndexSerializer,
)
from core.models.market_index.market_index import MarketIndex


class MarketIndexViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MarketIndex.objects.all()
    serializer_class = MarketIndexSerializer
    pagination_class = None
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = [
        "created",
        "modified",
        "name",
    ]
    ordering_fields = "__all__"
    ordering = ("symbol",)
    search_fields = ["symbol", "name"]
    lookup_field = "symbol"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MarketIndexDetailSerializer
        return self.serializer_class
