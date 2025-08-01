import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from core.models.stocks.stock_event import StockEventLog


class StockEventSerializer(serializers.Serializer):
    symbols = serializers.ListField(child=serializers.CharField())
    public_dates = serializers.ListField(child=serializers.DateField())


class StockEventDeleteView(APIView):

    def post(self, request, format=None):
        data = request.data
        serializer = StockEventSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            symbols = serializer.validated_data.get("symbols")
            public_dates = serializer.validated_data.get("public_dates")

            # delete stock event by given date range
            StockEventLog.objects.filter(
                public_date__in=public_dates, symbol__in=symbols
            ).delete()
        except Exception as e:
            logging.error(f"Error deleting stock event: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(status=status.HTTP_200_OK)
