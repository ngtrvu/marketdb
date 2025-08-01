from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework import serializers

from core.libs.intraday.intraday_manager import IntradayManager


class IntradayIndexerSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    price = serializers.FloatField()


class IntradayInitializerView(APIView):
    def post(self, request, format=None):
        manager = IntradayManager()
        manager.initialize()

        return Response(
            {"message": "Intraday data initialized successfully"},
            status=status.HTTP_200_OK,
        )


class IntradayIndexerView(APIView):
    def post(self, request, format=None):
        data = request.data
        serializer = IntradayIndexerSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        symbol = serializer.validated_data.get("symbol")
        price = serializer.validated_data.get("price")

        manager = IntradayManager()
        manager.add_price(
            symbol=symbol,
            price=price,
            timestamp=int(datetime.now().timestamp()),
        )
        return Response(
            {"message": "Intraday data indexed successfully"},
            status=status.HTTP_200_OK,
        )


class IntradayDetailView(RetrieveAPIView):
    lookup_field = "symbol"

    def retrieve(self, request, symbol, format=None):
        manager = IntradayManager()
        price, timestamp = manager.get_price(symbol=symbol)
        if not price or not timestamp:
            return Response(
                {"error": "No price found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "symbol": symbol,
                "price": price,
                "timestamp": timestamp,
            },
            status=status.HTTP_200_OK,
        )
