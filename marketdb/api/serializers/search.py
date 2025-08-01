from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from api.serializers.etf import ETFNestedSerializer
from api.serializers.stock import StockNestedSerializer
from core.models.etfs.etf import ETF
from core.models.mixin import AssetType
from core.models.search_index import SearchIndex
from core.models.stocks.stock import Stock


class SearchItemSerializer(serializers.ModelSerializer):
    detail = serializers.SerializerMethodField()
    photo = ImageHandlerSerializer()

    class Meta:
        model = SearchIndex
        fields = ["symbol", "detail", "type", "name", "brand_name", "photo"]

    def get_detail(self, obj):
        if obj.type == AssetType.STOCK:
            item = Stock(
                symbol=obj.symbol, name=obj.name, brand_name=obj.brand_name, photo=obj.photo
            )
            return StockNestedSerializer(item).data
        elif obj.type == AssetType.ETF:
            item = ETF(symbol=obj.symbol, name=obj.name, photo=obj.photo)
            return ETFNestedSerializer(item).data
        return None
