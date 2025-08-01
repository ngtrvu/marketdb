from rest_framework.generics import ListAPIView

from common.drfexts.serializers.filters import FilterSerializer
from api.serializers.screener import ScreenerSerializer
from core.services.etf.get_etfs import GetETFsService


class ScreenerETFsViewSet(ListAPIView):
    serializer_class = ScreenerSerializer

    def get_queryset(self):
        serializer = FilterSerializer(data=self.request.GET.dict())
        if not serializer.is_valid():
            raise ValueError("Request params invalid")

        fields = serializer.validated_data.get("fields", [])
        filters = serializer.validated_data.get("filters", [])
        sorts = serializer.validated_data.get("sorts", [])

        self.queryset = GetETFsService(fields=fields, filters=filters, sorts=sorts).call()
        return self.queryset
