from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from api.serializers.industry import NestedIndustrySerializer
from core.models.stocks.stock import Stock


class StockSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Stock
        fields = ["symbol", "name", "photo", "exchange", "brand_name"]


class StockDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()
    industry = NestedIndustrySerializer()
    super_sector = NestedIndustrySerializer()
    sector = NestedIndustrySerializer()
    sub_sector = NestedIndustrySerializer()

    class Meta:
        model = Stock
        fields = "__all__"


class StockNestedSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Stock
        fields = ["symbol", "name", "photo", "exchange", "brand_name"]
