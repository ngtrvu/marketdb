from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from core.models.cryptos.crypto_price_realtime import CryptoPriceRealtime
from api.serializers.crypto_price_realtime import CryptoPriceRealtimeSerializer


class CryptoPriceRealtimeDetailView(RetrieveAPIView):
    lookup_field = "symbol"
    queryset = CryptoPriceRealtime.objects.all()
    serializer_class = CryptoPriceRealtimeSerializer
    ordering = ('symbol',)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            context={},
        )
        return Response(serializer.data)
