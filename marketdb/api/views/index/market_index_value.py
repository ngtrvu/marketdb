from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from utils.date_range import get_range_dates
from core.models.market_index.market_index_value import MarketIndexValue
from core.models.market_index.market_index_daily import MarketIndexDaily
from api.serializers.market_index_value import (
    MarketIndexValueSerializer,
    MarketIndexDailySerializer,
)


class MarketIndexValueViewSet(ReadOnlyModelViewSet):
    serializer_class = MarketIndexValueSerializer
    queryset = MarketIndexValue.objects.all()
    lookup_field = "symbol"
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    ordering_fields = [
        "symbol",
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "total_volume",
        "total_value",
    ]
    ordering = ["symbol", "datetime"]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        current_date = instance.datetime.date()
        date_range = request.GET.get("date_range", "1m")
        from_date, to_date = get_range_dates(
            date_range=date_range, to_date=current_date
        )
        daily_data_queryset = MarketIndexDaily.objects.filter(
            symbol=instance.symbol,
            date__range=[from_date, to_date],
        ).order_by("-date")

        historical_serializer = MarketIndexDailySerializer(
            daily_data_queryset, many=True
        )

        data = {
            **serializer.data,
            "charts": historical_serializer.data,
        }

        return Response(data)
