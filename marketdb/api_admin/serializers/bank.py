from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.bank import Bank


class BankSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Bank
        fields = "__all__"
        singular_resource_name = "item"


class BankDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Bank
        fields = "__all__"
        singular_resource_name = "item"


class BankNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ["id", "title"]


class BankCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = "__all__"


class BankUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = "__all__"
