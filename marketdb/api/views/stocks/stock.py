from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.mixin import ContentStatusEnum
from core.models.stocks.stock import Stock
from api.serializers.stock import StockSerializer, StockDetailSerializer


class StockViewSet(ReadOnlyModelViewSet):
    lookup_field = "symbol"
    serializer_class = StockSerializer
    queryset = Stock.objects.select_related('industry').all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filterset_fields = ['exchange']
    ordering_fields = '__all__'
    ordering = ('-created',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StockDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        self.queryset = self.queryset.filter(exchange_status=Stock.STATUS_LISTED, status=ContentStatusEnum.PUBLISHED)
        return self.queryset
