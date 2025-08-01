from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.models.screener.collection import WatchlistCollection, ContentStatusEnum
from api.serializers.watchlist_collection import WatchlistCollectionSerializer


class WatchlistCollectionViewSet(ReadOnlyModelViewSet):
    serializer_class = WatchlistCollectionSerializer
    queryset = WatchlistCollection.objects.filter(status=ContentStatusEnum.PUBLISHED)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filterset_fields = ['product_type']
    ordering = ('-order',)
