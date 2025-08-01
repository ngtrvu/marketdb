from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.screener.collection import CollectionGroup


class CollectionGroupSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = CollectionGroup
        fields = "__all__"
        singular_resource_name = "item"


class CollectionGroupDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = CollectionGroup
        fields = "__all__"
        singular_resource_name = "item"


class CollectionGroupNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionGroup
        fields = ["id", "title"]


class CollectionGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionGroup
        fields = "__all__"


class CollectionGroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionGroup
        fields = "__all__"
