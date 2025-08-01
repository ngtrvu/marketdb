from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from common.auth.google import GoogleAuthentication
from api_admin.serializers.collection import (
    CollectionCreateSerializer,
    CollectionDetailSerializer,
    CollectionSerializer,
    CollectionUpdateSerializer,
)
from api_admin.serializers.collection_group import (
    CollectionGroupCreateSerializer,
    CollectionGroupDetailSerializer,
    CollectionGroupSerializer,
    CollectionGroupUpdateSerializer,
)
from core.models.screener.collection import Collection, CollectionGroup, ProductTypeEnum
from core.services.bank.get_banks import GetBanksService
from core.services.etf.get_etfs import GetETFsService
from core.services.fund.get_funds import GetFundsService
from core.services.stock.get_stocks import GetStocksService


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filter_fields = "__all__"
    ordering_fields = "__all__"
    ordering = ("-created",)
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    authentication_classes = [GoogleAuthentication]

    def get_serializer_class(self):
        if self.action == "create":
            return CollectionCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return CollectionUpdateSerializer
        elif self.action == "retrieve":
            return CollectionDetailSerializer
        return self.serializer_class


class CollectionGroupViewSet(viewsets.ModelViewSet):
    queryset = CollectionGroup.objects.all()
    serializer_class = CollectionGroupSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = "__all__"
    ordering = ("-created",)

    def get_serializer_class(self):
        if self.action == "create":
            return CollectionGroupCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return CollectionGroupUpdateSerializer
        elif self.action == "retrieve":
            return CollectionGroupDetailSerializer
        return self.serializer_class


class CollectionMetricsView(ListAPIView):
    def list(self, request, *args, **kwargs):
        mapping = {
            ProductTypeEnum.STOCK: GetStocksService,
            ProductTypeEnum.ETF: GetETFsService,
            ProductTypeEnum.BANK: GetBanksService,
            ProductTypeEnum.MUTUAL_FUND: GetFundsService,
        }
        type = kwargs["product_type"]
        service_cls = mapping.get(type)
        if not service_cls:
            raise ValueError("Collection type is invalid")

        data = service_cls().get_supported_fields(product_type=type)

        return Response({"items": data})


class CollectionOperatorsView(ListAPIView):
    def list(self, request, *args, **kwargs):
        mapping = {
            ProductTypeEnum.STOCK: GetStocksService,
            ProductTypeEnum.ETF: GetETFsService,
            ProductTypeEnum.BANK: GetBanksService,
            ProductTypeEnum.MUTUAL_FUND: GetFundsService,
        }

        type = kwargs["product_type"]
        service_cls = mapping.get(type)
        if not service_cls:
            raise ValueError("Collection type is invalid")

        data = service_cls().get_supported_operators()

        return Response({"items": data})
