from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.stock import (
    StockCreateSerializer,
    StockDetailSerializer,
    StockSerializer,
    StockUpdateSerializer,
)
from core.models.stocks.stock import Stock


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
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
    search_fields = ["name", "symbol", "brand_name"]
    authentication_classes = [GoogleAuthentication]

    def get_serializer_class(self):
        if self.action == "create":
            return StockCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return StockUpdateSerializer
        elif self.action == "retrieve":
            return StockDetailSerializer
        return self.serializer_class
