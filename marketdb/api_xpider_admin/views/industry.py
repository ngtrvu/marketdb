from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from common.auth.google import GoogleAuthentication
from common.drfexts.renderers.json_renderer import AdminPagination
from api_xpider_admin.serializers.industry import IndustrySerializer
from xpider.models.industry import Industry


class IndustryViewSet(ModelViewSet):
    serializer_class = IndustrySerializer
    queryset = Industry.objects.all()
    filterset_fields = ["level", "icb_code"]
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    pagination_class = AdminPagination
    authentication_classes = [GoogleAuthentication]
    ordering_fields = "__all__"
    ordering = ("-created",)
