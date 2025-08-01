from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.mixin import ContentStatusEnum
from core.models.etfs.etf import ETF
from api.serializers.etf import ETFSerializer, ETFDetailSerializer


class ETFViewSet(ReadOnlyModelViewSet):
    lookup_field = "symbol"
    serializer_class = ETFSerializer
    queryset = ETF.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    ordering = ('-created',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ETFDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        self.queryset = self.queryset.filter(exchange_status=ETF.STATUS_LISTED, status=ContentStatusEnum.PUBLISHED)
        return self.queryset
