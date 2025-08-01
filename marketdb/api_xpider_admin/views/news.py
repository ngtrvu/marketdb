from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from common.auth.google import GoogleAuthentication
from common.drfexts.renderers.json_renderer import AdminPagination
from api_xpider_admin.serializers.news import NewsPostSerializer
from xpider.models.news import NewsPost


class NewsPostViewSet(ModelViewSet):
    lookup_field = "uuid"
    serializer_class = NewsPostSerializer
    queryset = NewsPost.objects.exclude(published__isnull=True)
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = ["published"]
    pagination_class = AdminPagination
    authentication_classes = [GoogleAuthentication]
    ordering_fields = "__all__"
    ordering = ("-created",)
