from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status

from common.utils.datetime_util import (
    get_datetime_from_timestamp,
    VN_TIMEZONE,
)
from core.models.stocks.stock_price_realtime import StockPriceRealtime
from core.models.etfs.etf_price_chart import ETFPriceChart
from api.serializers.etf_price_realtime import (
    ETFPriceRealtimeDetailSerializer,
)
from core.services.stock.get_stock_price_realtime import (
    GetStockPriceRealTimeService,
)


class ETFPriceDetailView(RetrieveAPIView):
    lookup_field = "symbol"
    queryset = StockPriceRealtime.objects.all()
    serializer_class = ETFPriceRealtimeDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        symbol = self.kwargs["symbol"]
        service = GetStockPriceRealTimeService(symbol=symbol)

        instance = service.call()
        if not instance:
            return Response(
                {"error": service.error_message}, status=status.HTTP_400_BAD_REQUEST
            )

        chart_item = ETFPriceChart.objects.filter(symbol=instance.symbol).first()

        date_range = request.GET.get("date_range", "1d").lower()
        change_percentage, change_value, prices = self.__get_change_values(
            chart_item, date_range
        )

        serializer = self.get_serializer(
            instance,
            context={
                "change_percentage": change_percentage,
                "change_value": change_value,
                "prices": prices,
                "date_range": date_range,
            },
        )
        return Response(serializer.data)

    def __get_change_values(self, chart_item: ETFPriceChart, date_range: str):
        change_percentage: str = None
        change_value: str = None
        prices: list = []

        if date_range == "1d":
            change_value = chart_item.price - chart_item.reference
            change_percentage = (change_value / chart_item.reference) * 100
            prices = []  # not support for intraday data
        elif date_range == "1w":
            change_percentage = chart_item.change_percentage_1w
            change_value = chart_item.price_1w
            prices = chart_item.movement_1w
        elif date_range == "1m":
            change_percentage = chart_item.change_percentage_1m
            change_value = chart_item.price_1m
            prices = chart_item.movement_1m
        elif date_range == "3m":
            change_percentage = chart_item.change_percentage_3m
            change_value = chart_item.price_3m
            prices = chart_item.movement_3m
        elif date_range == "6m":
            change_percentage = chart_item.change_percentage_6m
            change_value = chart_item.price_6m
            prices = chart_item.movement_6m
        elif date_range == "1y":
            change_percentage = chart_item.change_percentage_1y
            change_value = chart_item.price_1y
            prices = chart_item.movement_1y
        elif date_range == "3y":
            change_percentage = chart_item.change_percentage_3y
            change_value = chart_item.price_3y
            prices = chart_item.movement_3y
        elif date_range == "5y":
            change_percentage = chart_item.change_percentage_5y
            change_value = chart_item.price_5y
            prices = chart_item.movement_5y
        elif date_range == "ytd":
            change_percentage = chart_item.change_percentage_ytd
            change_value = chart_item.price_ytd
            prices = chart_item.movement_ytd
        elif date_range == "all":
            change_percentage = chart_item.change_percentage_inception_date
            change_value = chart_item.price_inception_date
            prices = chart_item.movement_all
        else:
            change_value = chart_item.price - chart_item.reference
            change_percentage = (change_value / chart_item.reference) * 100
            prices = []  # not support for intraday data

        chart_prices = self.__ensure_timestamp_vntime(prices)
        chart_prices = chart_prices + [
            {"c": chart_item.price, "t": int(chart_item.datetime.timestamp())}
        ]
        return change_percentage, change_value, chart_prices

    def __ensure_timestamp_vntime(self, movement: list) -> list:
        new_movement = []
        for d in movement:
            value = get_datetime_from_timestamp(d["t"], tz=VN_TIMEZONE)
            d["t"] = int(value.timestamp())
            new_movement.append(d)
        return new_movement
