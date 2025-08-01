import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from core.libs.intraday.intraday_manager import IntradayManager
from api.serializers.stock_price_intraday import StockOrderStatsSerializer
from core.models.stocks.stock import Stock


class StockOrderStatsView(GenericAPIView):
    lookup_field = 'symbol'
    serializer_class = StockOrderStatsSerializer
    queryset = Stock.objects.all()
    ordering = ('symbol',)

    def get(self, request, symbol):
        self.get_object()

        price_volume_agg = IntradayManager().get_and_build_chart_intraday(symbol=symbol)
        order_stats = []
        for price, volume in price_volume_agg.items():
            if self.get_serializer(data={'price': price, 'volume': volume}).is_valid(raise_exception=False):
                order_stats.append({'price': price, 'volume': volume})
        
        try:
            serializer = self.get_serializer(order_stats, many=True)
        except:
            return Response(data={'items': []}, status=status.HTTP_200_OK)
        return Response(data={'items': serializer.data}, status=status.HTTP_200_OK)
