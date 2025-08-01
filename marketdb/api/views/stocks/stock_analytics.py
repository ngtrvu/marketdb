from django.db.models import Max, F
from django.http import Http404
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.response import Response

from common.gcs.utils import get_json
from api.serializers.stock_fa import StockFASerializer
from core.models import StockFA


class StockFAViewSet(RetrieveAPIView):
    lookup_field = "symbol"
    serializer_class = StockFASerializer
    queryset = StockFA.objects.all()
    ordering = ('symbol',)

    def get_object(self):
        # custom filter
        filter_kwargs = {}
        symbol = self.kwargs.get(self.lookup_field, None).upper()
        if symbol:
            filter_kwargs = {"symbol": symbol}

        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        symbol = kwargs.get(self.lookup_field, None).upper()
        if not instance or not symbol:
            return Response(
                {"error": "Not found fundamental"}, status=status.HTTP_404_NOT_FOUND
            )

        max_date = StockFA.objects.aggregate(Max('date')).get("date__max")
        queryset = self.get_queryset().filter(symbol=symbol, date__gte=max_date).first()
        if not queryset:
            no_data = {
                "items": [
                    {
                        "label": "Mã Cổ Phiếu",
                        "key": "symbol",
                        "value": symbol,
                        "datatype": None
                    },
                    {
                        "label": "Trạng thái",
                        "key": "date",
                        "value": "Đang cập nhật",
                        "datatype": None
                    }
                ]
            }
            return Response(data=no_data)

        serializer = StockFASerializer(
            instance=queryset, many=False, context={}
        )
        return Response(data=serializer.data)


class StockScoringView(RetrieveAPIView):
    lookup_field = 'symbol'

    def get(self, request, *args, **kwargs):
        symbol = self.kwargs[self.lookup_field].upper()

        bucket_name = "stock_analytics"
        base_path = "analytics"
        score_path = f"{base_path}/stock_scoring/scoring/latest/{symbol}_scoring.json"
        score_data = get_json(bucket_name=bucket_name, source=score_path)

        if not score_data or not len(score_data) or not score_data[0].get("stag_score"):
            raise Http404

        detail_filename = f"{symbol}_scoring_interpretable_features.json"
        detail_path = f"{base_path}/stock_scoring/scoring/latest/{detail_filename}"
        detail_data = get_json(bucket_name=bucket_name, source=detail_path)

        if not detail_data or not len(detail_data) or "symbol" not in detail_data[0]:
            raise Http404

        return Response({'score': score_data[0], 'detail': detail_data[0]})
