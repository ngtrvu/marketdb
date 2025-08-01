from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.industry import (
    IndustryCreateSerializer,
    IndustryDetailSerializer,
    IndustrySerializer,
    IndustryUpdateSerializer,
)
from core.models.industries.industry import Industry


class IndustryViewSet(viewsets.ModelViewSet):
    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = {
        "level": ["exact"],
        "status": ["exact"],
        "icb_code": ["exact"],
    }
    ordering_fields = "__all__"
    ordering = ("-created",)
    search_fields = ["name", "icb_code", "slug"]
    authentication_classes = [GoogleAuthentication]

    def get_serializer_class(self):
        if self.action == "create":
            return IndustryCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return IndustryUpdateSerializer
        elif self.action == "retrieve":
            return IndustryDetailSerializer
        return self.serializer_class
