from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from common.drfexts.renderers.json_renderer import AdminPagination
from api_admin.serializers.stock_event import (
    StockEventCreateSerializer,
    StockEventDetailSerializer,
    StockEventSerializer,
    StockEventUpdateSerializer,
    StockEventLogDetailSerializer,
    StockEventLogSerializer,
)
from core.models.stocks.stock_event import StockEvent, StockEventLog


class StockEventViewSet(viewsets.ModelViewSet):
    queryset = StockEvent.objects.all()
    serializer_class = StockEventSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = {
        "record_date": ["gte", "lte", "exact"],
        "exright_date": ["gte", "lte", "exact"],
        "issue_date": ["gte", "lte", "exact"],
        "symbol": ["exact"],
        "name": ["exact"],
    }
    ordering_fields = "__all__"
    ordering = ("-public_date",)
    search_fields = ["title", "symbol"]
    authentication_classes = [GoogleAuthentication]
    pagination_class = AdminPagination

    def get_serializer_class(self):
        if self.action == "create":
            return StockEventCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return StockEventUpdateSerializer
        elif self.action == "retrieve":
            return StockEventDetailSerializer
        return self.serializer_class


class StockEventLogViewSet(viewsets.ModelViewSet):
    queryset = StockEventLog.objects.all()
    serializer_class = StockEventLogSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = {
        "record_date": ["gte", "lte", "exact"],
        "exright_date": ["gte", "lte", "exact"],
        "issue_date": ["gte", "lte", "exact"],
        "symbol": ["exact"],
        "name": ["exact"],
    }
    ordering_fields = "__all__"
    ordering = ("-public_date",)
    search_fields = ["title", "symbol"]
    authentication_classes = [GoogleAuthentication]
    pagination_class = AdminPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StockEventLogDetailSerializer
        return self.serializer_class
