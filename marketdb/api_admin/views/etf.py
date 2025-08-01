from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.etf import (
    ETFCreateSerializer,
    ETFDetailSerializer,
    ETFSerializer,
    ETFUpdateSerializer,
)
from core.models.etfs.etf import ETF


class ETFViewSet(viewsets.ModelViewSet):
    queryset = ETF.objects.all()
    serializer_class = ETFSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = [
        "status",
        "exchange",
        "created",
        "modified",
        "outstanding_shares",
        "name",
        "inception_date",
    ]
    ordering_fields = "__all__"
    ordering = ("-created",)
    search_fields = ["name", "symbol"]
    authentication_classes = [GoogleAuthentication]

    def get_serializer_class(self):
        if self.action == "create":
            return ETFCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return ETFUpdateSerializer
        elif self.action == "retrieve":
            return ETFDetailSerializer
        return self.serializer_class
