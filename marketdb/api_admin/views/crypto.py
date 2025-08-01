from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.crypto import (
    CryptoCreateSerializer,
    CryptoDetailSerializer,
    CryptoSerializer,
    CryptoUpdateSerializer,
)
from core.models.cryptos.crypto import Crypto


class CryptoViewSet(viewsets.ModelViewSet):
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer
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
            return CryptoCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return CryptoUpdateSerializer
        elif self.action == "retrieve":
            return CryptoDetailSerializer
        return self.serializer_class
