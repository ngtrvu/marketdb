from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from api_xpider_admin.serializers.sources import PageSerializer, PublisherSerializer
from api_xpider_admin.serializers.news import NewsPostSerializer
from xpider.models.sources import LandingPage, Publisher


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LandingPage.objects.all()
    serializer_class = PageSerializer
    pagination_class = None
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = [
        "language",
        "category",
    ]
    ordering_fields = "__all__"
    ordering = ("title",)


class PublisherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    pagination_class = None
