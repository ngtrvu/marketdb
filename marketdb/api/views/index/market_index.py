from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.market_index.market_index import MarketIndex
from api.serializers.market_index import MarketIndexSerializer


class MarketIndexViewSet(ReadOnlyModelViewSet):
    lookup_field = "symbol"
    serializer_class = MarketIndexSerializer
    queryset = MarketIndex.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    ordering_fields = ["symbol", "name", "modified"]
    ordering = ['symbol']
