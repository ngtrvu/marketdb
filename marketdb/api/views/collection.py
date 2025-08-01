from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from core.models.screener.collection import Collection, ProductTypeEnum, ContentStatusEnum, Metric
from api.serializers.collection import (
    CollectionSerializer, CollectionDetailSerializer, CollectionItemsSerializer
)
from core.services.stock.get_stocks import GetStocksService
from core.services.etf.get_etfs import GetETFsService
from core.services.fund.get_funds import GetFundsService
from core.services.bank.get_banks import GetBanksService


class CollectionViewSet(ReadOnlyModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.filter(status=ContentStatusEnum.PUBLISHED)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filterset_fields = ['product_type']
    ordering = ('-order',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectionDetailSerializer
        return self.serializer_class


class CollectionsByContentTypeView(ListAPIView):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.filter(status=ContentStatusEnum.PUBLISHED)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filterset_fields = ['product_type']
    ordering = ('-order',)

    def get_queryset(self):
        self.queryset = self.queryset.filter(content_type=self.kwargs['content_type'])
        return self.queryset


class CollectionItemsView(ListAPIView):
    lookup_field = "symbol"
    serializer_class = CollectionItemsSerializer

    def get_collection(self):
        return get_object_or_404(Collection, pk=self.kwargs['collection_id'], status=ContentStatusEnum.PUBLISHED)

    def get_queryset(self):
        collection = self.get_collection()
        mapping = {
            ProductTypeEnum.STOCK: GetStocksService,
            ProductTypeEnum.ETF: GetETFsService,
            ProductTypeEnum.BANK: GetBanksService,
            ProductTypeEnum.MUTUAL_FUND: GetFundsService,
        }

        service_cls = mapping.get(collection.product_type)
        if not service_cls:
            raise ValueError("Collection type is invalid")

        self.queryset = service_cls(fields=collection.field_params, filters=collection.filter_params, sorts=collection.sort_params).call()
        return self.queryset[:collection.limit]

    def get_serializer_context(self):
        collection = self.get_collection()
        data = Metric.objects.filter(product_type=collection.product_type).all()
        metrics = {}

        for item in data:
            if item.name in collection.field_params:
                metrics[item.name] = {
                    'field': item.name,
                    'label': item.label,
                    'type': item.data_type,
                }

        context = super(CollectionItemsView, self).get_serializer_context()
        context.update({"metrics": metrics})
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response({'items': serializer.data})
