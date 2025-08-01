from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from api_internal.serializers.fund_analytics import (
    FundAnalyticsDetailSerializer
)
from core.models.funds.fund_price_analytics import FundNavAnalytics


class FundAnalyticsDetailView(ReadOnlyModelViewSet):
    queryset = FundNavAnalytics.objects.all()
    serializer_class = FundAnalyticsDetailSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = "__all__"
    ordering = ("symbol",)
    search_fields = ["symbol"]
    lookup_field = "symbol"

    def get_serializer_class(self):
        if self.action == "list":
            return FundAnalyticsDetailSerializer
        elif self.action == "retrieve":
            return FundAnalyticsDetailSerializer

        return self.serializer_class
