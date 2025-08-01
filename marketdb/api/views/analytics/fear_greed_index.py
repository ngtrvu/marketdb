import datetime

from rest_framework import filters
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from common.utils.datetime_util import get_datetime_now, VN_TIMEZONE
from common.utils.date_ranges import DateRangeUtils
from core.models.market.market_analytics import FearGreedIndexDaily
from api.serializers.fear_greed_index import (
    FearGreedIndexDetailSerializer,
    FearGreedIndexHistoricalValuesSerializer,
    FearGreedIndexDailyListSerializer,
)


class FearGreedIndexView(RetrieveAPIView):
    queryset = FearGreedIndexDaily.objects.all()
    serializer_class = FearGreedIndexDetailSerializer
    ordering = ('-created',)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        obj = queryset.order_by('-date', '-datetime').first()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class FearGreedIndexDailyListView(ListAPIView):
    queryset = FearGreedIndexDaily.objects.all()
    serializer_class = FearGreedIndexDailyListSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = ('date',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FearGreedIndexHistoricalValuesView(ListAPIView):
    queryset = FearGreedIndexDaily.objects.all()
    serializer_class = FearGreedIndexHistoricalValuesSerializer

    def list(self, request, *args, **kwargs):

        fear_greed_index_1d = self.get_score(date_range="1d")
        fear_greed_index_1w = self.get_score(date_range="1w")
        fear_greed_index_1m = self.get_score(date_range="1m")
        fear_greed_index_1y = self.get_score(date_range="1y")
        data = [
            {
                'label': 'Phiên trước',
                'fear_greed_index': fear_greed_index_1d
            },
            {
                'label': 'Tuần trước',
                'fear_greed_index': fear_greed_index_1w
            },
            {
                'label': 'Tháng trước',
                'fear_greed_index': fear_greed_index_1m
            },
            {
                'label': 'Năm trước',
                'fear_greed_index': fear_greed_index_1y
            },
        ]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

    def get_score(self, date_range: str):
        queryset = self.get_queryset()
        today = get_datetime_now(tz=VN_TIMEZONE).date()
        from_date, to_date = DateRangeUtils().get_date_range(date_range=date_range, to_date=today)
        return queryset.filter(date__lt=from_date).order_by('-date', '-datetime').first()

