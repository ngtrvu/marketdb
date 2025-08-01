from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.screener.collection import Collection, Metric


class CollectionSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Collection
        fields = ["id", "title", "slug", "photo", "excerpt", "created", "modified", "product_type"]


class CollectionDetailSerializer(serializers.ModelSerializer):
    photo = ImageHandlerSerializer()

    class Meta:
        model = Collection
        fields = [
            "id",
            "title",
            "slug",
            "photo",
            "excerpt",
            "description",
            "created",
            "modified",
            "product_type",
            "field_params",
            "filter_params",
            "sort_params",
        ]


class CollectionItemsSerializer(serializers.Serializer):
    symbol = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    photo = ImageHandlerSerializer()
    metrics = serializers.SerializerMethodField()

    def get_symbol(self, instance):
        return instance.symbol

    def get_name(self, instance):
        return instance.name

    def get_metrics(self, instance):
        metrics = self.context.get("metrics", {})

        result = []
        for field, metric in metrics.items():
            value = getattr(instance, field) if hasattr(instance, field) else None
            result.append(
                {
                    "key": field,
                    "label": metric.get("label", field),
                    "value": value,
                    "type": metric.get("type", "string"),
                }
            )

        return result
