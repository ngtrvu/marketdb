from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.funds.fund import MutualFund


class MutualFundSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = MutualFund
        fields = "__all__"
        singular_resource_name = "item"


class MutualFundDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = MutualFund
        fields = "__all__"
        singular_resource_name = "item"


class MutualFundNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = MutualFund
        fields = ["id", "name", "symbol"]


class MutualFundCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MutualFund
        fields = "__all__"


class MutualFundUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MutualFund
        fields = "__all__"
