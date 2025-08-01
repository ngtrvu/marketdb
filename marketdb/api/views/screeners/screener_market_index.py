from rest_framework.generics import ListAPIView

from common.drfexts.serializers.filters import FilterSerializer
from api.serializers.screener import ScreenerSerializer
from core.services.market_index.get_market_indexes import GetMarketIndexesService


class ScreenerMarketIndexesViewSet(ListAPIView):
    serializer_class = ScreenerSerializer

    def get_queryset(self):
        serializer = FilterSerializer(data=self.request.GET.dict())
        if not serializer.is_valid():
            raise ValueError("Request params invalid")

        fields = serializer.validated_data.get("fields", [])
        filters = serializer.validated_data.get("filters", [])
        sorts = serializer.validated_data.get("sorts", [])

        self.queryset = GetMarketIndexesService(fields=fields, filters=filters, sorts=sorts).call()
        return self.queryset
