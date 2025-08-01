from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from core.models.stocks.stock_price_chart import StockPriceChart
from api.serializers.stock_price_chart import StockPriceChartMovementSerializer
from core.services.stock.get_stock_chart import GetStockChartService


class StockPriceChartView(RetrieveAPIView):
    lookup_field = "symbol"
    serializer_class = StockPriceChartMovementSerializer
    queryset = StockPriceChart.objects.all()
    ordering = ('symbol',)

    def retrieve(self, request, *args, **kwargs):
        self.get_object()

        date_range = request.GET.get('date_range')
        symbol = kwargs.get('symbol')

        get_chart = GetStockChartService(
            symbol=symbol, date_range=date_range
        )
        success = get_chart.call()
        if not success:
            return Response(data={"error": get_chart.get_error_message()},
                            status=status.HTTP_404_NOT_FOUND)

        chart_data = {
            "symbol": symbol,
            "date_range": date_range,
            "price": get_chart.price,
            "datetime": get_chart.datetime,
            "change_value": get_chart.change_value,
            "change_percentage": get_chart.change_percentage,
            "prices": get_chart.movement
        }

        serializer = self.get_serializer(chart_data, many=False)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
