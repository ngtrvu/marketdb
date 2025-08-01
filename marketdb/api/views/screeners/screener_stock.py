from rest_framework.generics import ListAPIView

from common.drfexts.serializers.filters import FilterSerializer
from api.serializers.screener import ScreenerSerializer
from core.services.stock.get_stocks import GetStocksService


class ScreenerStocksViewSet(ListAPIView):
    serializer_class = ScreenerSerializer

    def get_queryset(self):
        serializer = FilterSerializer(data=self.request.GET.dict())
        if not serializer.is_valid():
            raise ValueError("Request params invalid")

        fields, filters, sorts = (
            serializer.validated_data.get("fields", []),
            serializer.validated_data.get("filters", []),
            serializer.validated_data.get("sorts", []),
        )
        self.queryset = GetStocksService(fields=fields, filters=filters, sorts=sorts).call()
        return self.queryset
