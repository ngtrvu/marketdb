from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from common.pagination import CustomPagination
from core.models.mixin import ContentStatusEnum
from core.models.funds.fund import MutualFund
from api.serializers.fund import (
    MutualFundSerializer,
    MutualFundDetailSerializer,
)


class MutualFundViewSet(ReadOnlyModelViewSet):
    lookup_field = "symbol"
    serializer_class = MutualFundSerializer
    queryset = MutualFund.objects.all()
    pagination_class = CustomPagination
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    ordering = ("-created",)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MutualFundDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        self.queryset = self.queryset.filter(status=ContentStatusEnum.PUBLISHED)
        return self.queryset
