from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.stock_analytics import StockFASerializer
from core.models.stocks.stock_analytics import StockFA


class StockFAViewSet(viewsets.ModelViewSet):
    queryset = StockFA.objects.all()
    serializer_class = StockFASerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = {
        "symbol": ["exact"],
        "date": ["exact", "lte", "gte"],
    }
    ordering_fields = "__all__"
    ordering = ("-created",)
    search_fields = ["company_type", "symbol"]
    authentication_classes = [GoogleAuthentication]
