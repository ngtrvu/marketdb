from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.bank import Bank
from api.serializers.bank import BankSerializer, BankDetailSerializer


class BankViewSet(ReadOnlyModelViewSet):
    serializer_class = BankSerializer
    queryset = Bank.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    ordering = ('-created',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BankDetailSerializer
        return self.serializer_class
