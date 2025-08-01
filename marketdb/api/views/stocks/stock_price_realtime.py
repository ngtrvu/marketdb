from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status

from core.models.stocks.stock_price_realtime import StockPriceRealtime
from core.models.stocks.stock_price_chart import StockPriceChart
from core.models.stocks.stock_price_analytics import StockPriceAnalytics
from api.serializers.stock_price_realtime import StockPriceRealtimeDetailSerializer
from core.services.stock.get_stock_price_realtime import GetStockPriceRealTimeService


class StockPriceRealtimeDetailView(RetrieveAPIView):
    lookup_field = "symbol"
    queryset = StockPriceRealtime.objects.all()
    serializer_class = StockPriceRealtimeDetailSerializer
    ordering = ('symbol',)

    def retrieve(self, request, *args, **kwargs):
        symbol = self.kwargs['symbol']
        service = GetStockPriceRealTimeService(symbol=symbol)

        instance = service.call()
        if not instance:
            return Response({"error": service.error_message}, status=status.HTTP_400_BAD_REQUEST)

        charts = StockPriceChart.objects.filter(symbol=instance.symbol).first()
        analytics = StockPriceAnalytics.objects.filter(symbol=instance.symbol).first()

        serializer = self.get_serializer(
            instance,
            context={
                'charts': charts,
                'analytics': analytics,
                'date_range': request.GET.get('date_range', '1d')
            },
        )
        return Response(serializer.data)
