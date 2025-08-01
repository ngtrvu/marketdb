from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.bank import (
    BankCreateSerializer,
    BankDetailSerializer,
    BankSerializer,
    BankUpdateSerializer,
)
from core.models.bank import Bank


class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all().order_by("id")
    serializer_class = BankSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = "__all__"
    search_fields = ["title", "symbol", "slug"]
    authentication_classes = [GoogleAuthentication]
    ordering = ["-created"]

    def get_serializer_class(self):
        if self.action == "create":
            return BankCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return BankUpdateSerializer
        elif self.action == "retrieve":
            return BankDetailSerializer
        return self.serializer_class
