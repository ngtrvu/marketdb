from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ReadOnlyModelViewSet

from common.auth.google import GoogleAuthentication
from api_admin.serializers.fund_analytics import (
    FundAnalyticsSerializer,
    FundAnalyticsDetailSerializer
)
from core.models.funds.fund_price_analytics import FundNavAnalytics


class FundAnalyticsDetailViewSet(ReadOnlyModelViewSet):
    queryset = FundNavAnalytics.objects.all()
    serializer_class = FundAnalyticsSerializer
    detail_serializer_class = FundAnalyticsDetailSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = "__all__"
    ordering = ("-annualized_return_percentage",)
    search_fields = ["symbol"]
    lookup_field = "symbol"
    authentication_classes = [GoogleAuthentication]

    def get_serializer_class(self):
        if self.action == "list":
            return FundAnalyticsSerializer
        elif self.action == "retrieve":
            return FundAnalyticsDetailSerializer

        return self.serializer_class
