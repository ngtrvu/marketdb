from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.funds.fund import MutualFund


class MutualFundSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = MutualFund
        fields = ["symbol", "name", "photo", "type"]


class MutualFundDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = MutualFund
        fields = "__all__"


class MutualFundNestedSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = MutualFund
        fields = ["symbol", "name", "photo"]
