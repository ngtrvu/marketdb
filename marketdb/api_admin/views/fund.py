from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.fund import (
    MutualFundCreateSerializer,
    MutualFundDetailSerializer,
    MutualFundSerializer,
    MutualFundUpdateSerializer,
)
from core.models.funds.fund import MutualFund


class MutualFundViewSet(viewsets.ModelViewSet):
    queryset = MutualFund.objects.all()
    serializer_class = MutualFundSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = "__all__"
    ordering = ("-created",)
    search_fields = ["name", "symbol"]
    authentication_classes = [GoogleAuthentication]

    def get_serializer_class(self):
        if self.action == "create":
            return MutualFundCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return MutualFundUpdateSerializer
        elif self.action == "retrieve":
            return MutualFundDetailSerializer
        return self.serializer_class
