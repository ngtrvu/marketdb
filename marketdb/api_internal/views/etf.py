from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from api_admin.serializers.etf import ETFDetailSerializer, ETFSerializer
from core.models.etfs.etf import ETF


class ETFViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ETF.objects.all()
    serializer_class = ETFSerializer
    pagination_class = None
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = [
        "status",
        "exchange_status",
        "exchange",
        "created",
        "modified",
        "outstanding_shares",
        "name",
        "inception_date",
    ]
    ordering_fields = "__all__"
    ordering = ("symbol",)
    search_fields = ["symbol", "name"]
    lookup_field = "symbol"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ETFDetailSerializer
        return self.serializer_class
