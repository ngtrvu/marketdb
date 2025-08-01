from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from api.serializers.screener import ScreenerSerializer
from api_admin.serializers.collection_group import CollectionGroupNestedSerializer
from core.models.screener.collection import Collection, ProductTypeEnum
from core.services.bank.get_banks import GetBanksService
from core.services.etf.get_etfs import GetETFsService
from core.services.fund.get_funds import GetFundsService
from core.services.stock.get_stocks import GetStocksService


class CollectionSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()
    group = CollectionGroupNestedSerializer()

    class Meta:
        model = Collection
        fields = "__all__"
        singular_resource_name = "item"


class CollectionDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()
    preview_list = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = "__all__"
        singular_resource_name = "item"

    def get_preview_list(self, obj):
        mapping = {
            ProductTypeEnum.STOCK: GetStocksService,
            ProductTypeEnum.ETF: GetETFsService,
            ProductTypeEnum.BANK: GetBanksService,
            ProductTypeEnum.MUTUAL_FUND: GetFundsService,
        }
        if obj.product_type and mapping.get(obj.product_type):
            service_cls = mapping.get(obj.product_type)
            queryset = service_cls(
                fields=obj.field_params, filters=obj.filter_params, sorts=obj.sort_params
            ).call()
            return ScreenerSerializer(queryset, many=True).data

        return []


class CollectionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "title"]


class CollectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"


class CollectionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"
