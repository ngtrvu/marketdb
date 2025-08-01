from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.market_index.market_index_value import MarketIndexValue
from api.serializers.market_index_value import MarketIndexValueSerializer


class MarketTrendingView(GenericViewSet, ListModelMixin):
    lookup_field = "symbol"
    serializer_class = MarketIndexValueSerializer
    queryset = MarketIndexValue.objects.all()
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_fields = ["exchange", "symbol"]
    ordering_fields = ["ordering", "total_value", "volume"]
    ordering = (
        "-ordering",
        "-total_value",
    )
