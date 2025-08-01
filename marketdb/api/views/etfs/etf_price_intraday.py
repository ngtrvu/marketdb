from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from core.libs.intraday.intraday_manager import IntradayManager
from api.serializers.etf_price_intraday import ETFOrderStatsSerializer
from core.models.etfs.etf import ETF


class ETFOrderStatsView(GenericAPIView):
    lookup_field = 'symbol'
    serializer_class = ETFOrderStatsSerializer
    queryset = ETF.objects.all()
    ordering = ('symbol',)

    def get(self, request, symbol):
        self.get_object()

        price_volume_agg = IntradayManager().get_and_build_chart_intraday(symbol=symbol)
        order_stats = []
        for price, volume in price_volume_agg.items():
            order_stats.append({"price": price, "volume": volume})

        serializer = self.get_serializer(order_stats, many=True)
        return Response(data={'items': serializer.data}, status=status.HTTP_200_OK)
