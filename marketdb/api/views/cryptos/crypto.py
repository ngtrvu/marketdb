from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.mixin import ContentStatusEnum
from core.models.cryptos.crypto import Crypto
from api.serializers.crypto import CryptoSerializer, CryptoDetailSerializer


class CryptoViewSet(ReadOnlyModelViewSet):
    lookup_field = "symbol"
    serializer_class = CryptoSerializer
    queryset = Crypto.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    ordering = ('market_cap_rank',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CryptoDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        self.queryset = self.queryset.filter(status=ContentStatusEnum.PUBLISHED)
        return self.queryset
