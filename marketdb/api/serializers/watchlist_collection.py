from rest_framework import serializers

from common.drfexts.serializers.fields import ImageHandlerSerializer
from core.models.screener.collection import Metric, ProductTypeEnum, WatchlistCollection
from core.services.bank.get_banks import GetBanksService
from core.services.etf.get_etfs import GetETFsService
from core.services.fund.get_funds import GetFundsService
from core.services.stock.get_stocks import GetStocksService


class WatchlistCollectionItemsSerializer(serializers.Serializer):
    symbol = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()
    photo = ImageHandlerSerializer()
    metrics = serializers.SerializerMethodField()

    def get_symbol(self, instance):
        return instance.symbol

    def get_name(self, instance):
        return instance.name

    def get_product_type(self, instance):
        return self.context.get("product_type", "")

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


class WatchlistCollectionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = WatchlistCollection
        fields = ["id", "title", "photo", "created", "modified", "product_type", "items"]

    def get_items(self, instance):
        data = Metric.objects.filter(product_type=instance.product_type).all()
        metrics = {}

        for item in data:
            if item.name in instance.field_params:
                metrics[item.name] = {
                    "field": item.name,
                    "label": item.label,
                    "type": item.data_type,
                }

        mapping = {
            ProductTypeEnum.STOCK: GetStocksService,
            ProductTypeEnum.ETF: GetETFsService,
            ProductTypeEnum.BANK: GetBanksService,
            ProductTypeEnum.MUTUAL_FUND: GetFundsService,
        }
        service_cls = mapping.get(instance.product_type)
        if not service_cls:
            raise ValueError("Collection type is invalid")

        queryset = service_cls(
            fields=instance.field_params, filters=instance.filter_params, sorts=instance.sort_params
        ).call()
        return WatchlistCollectionItemsSerializer(
            queryset, many=True, context={"metrics": metrics, "product_type": instance.product_type}
        ).data
