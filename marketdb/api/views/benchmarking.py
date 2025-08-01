import math
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from api.serializers.benchmarking import BenchmarkingSerializer
from api.serializers.stock_price_realtime import PriceRealtimeSerializer
from core.services.industry.get_industries import GetIndustriesService
from core.services.market_index.get_market_indexes import (
    GetMarketIndexesService,
)
from core.models.stocks.stock_price_analytics import StockPriceAnalytics
from core.models.stocks.stock_price_chart import StockPriceChart
from core.models.stocks.stock_price_realtime import StockPriceRealtime
from api.serializers.stock_price_realtime import (
    StockPriceRealtimeDetailSerializer,
)
from core.services.stock.get_stock_price_realtime import (
    GetStockPriceRealTimeService,
)


class BenchmarkingView(ListAPIView):

    def get_date_range(self, criteria):
        mapping = {
            "change_percentage_1d": "1d",
            "change_percentage_1w": "1w",
            "change_percentage_1m": "1m",
            "change_percentage_3m": "3m",
            "change_percentage_1y": "1y",
            "change_percentage_5y": "5y",
        }
        return mapping.get(criteria)

    def get_stock_performance(self, symbols, criteria, data_type):
        date_range = self.get_date_range(criteria)
        data = []

        for symbol in symbols:
            instance = GetStockPriceRealTimeService(symbol=symbol).call()
            analytics = StockPriceAnalytics.objects.filter(
                symbol=instance.symbol
            ).first()
            charts = StockPriceChart.objects.filter(symbol=instance.symbol).first()
            serializer = StockPriceRealtimeDetailSerializer(
                instance,
                context={
                    "charts": charts,
                    "analytics": analytics,
                    "date_range": date_range,
                },
            )

            data.append(
                {
                    "name": serializer.data["symbol"],
                    "symbol": serializer.data["symbol"],
                    criteria: serializer.data["change_percentage"],
                    "type": data_type,
                }
            )

        return data

    def get_industry_performance(self, industries, criteria):
        if len(industries) == 0:
            return []

        data = []

        items = GetIndustriesService(
            fields=[criteria],
            filters=[
                {"name": "icb_code", "operator": "in", "value": ";".join(industries)}
            ],
        ).call()

        for item in items:
            criteria_value = (
                getattr(item, criteria) if hasattr(item, criteria) else None
            )
            criteria_value = (
                None
                if criteria_value and math.isnan(criteria_value)
                else criteria_value
            )
            data.append(
                {
                    "name": item.name,
                    "symbol": item.icb_code,
                    criteria: criteria_value,
                    "type": "industry",
                }
            )

        return data

    def get_market_index_performance(self, market_indexes, criteria):
        if len(market_indexes) == 0:
            return []

        data = []
        if criteria == "change_percentage_1d":
            items = StockPriceRealtime.objects.filter(symbol__in=market_indexes)
            for item in items:
                serializer = PriceRealtimeSerializer(item)

                data.append(
                    {
                        "name": serializer.data["symbol"],
                        "symbol": serializer.data["symbol"],
                        criteria: serializer.data["change_percentage"],
                        "type": "market_index",
                    }
                )

            return data

        items = GetMarketIndexesService(
            fields=[criteria],
            filters=[
                {"name": "symbol", "operator": "in", "value": ";".join(market_indexes)}
            ],
        ).call()

        for item in items:
            criteria_value = (
                getattr(item, criteria) if hasattr(item, criteria) else None
            )
            criteria_value = (
                None
                if criteria_value and math.isnan(criteria_value)
                else criteria_value
            )
            data.append(
                {
                    "name": item.name,
                    "symbol": item.symbol,
                    criteria: criteria_value,
                    "type": "market_index",
                }
            )

        return data

    def list(self, request, *args, **kwargs):
        serializer = BenchmarkingSerializer(data=self.request.GET.dict())
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = []

        criteria = serializer.validated_data.get("criteria", "")
        stocks = serializer.validated_data.get("stocks", [])
        etfs = serializer.validated_data.get("etfs", [])
        industries = serializer.validated_data.get("industries", [])
        market_indexes = serializer.validated_data.get("market_indexes", [])

        data += self.get_stock_performance(
            symbols=stocks, criteria=criteria, data_type="stock"
        )
        data += self.get_stock_performance(
            symbols=etfs, criteria=criteria, data_type="etf"
        )
        data += self.get_industry_performance(industries=industries, criteria=criteria)
        data += self.get_market_index_performance(
            market_indexes=market_indexes, criteria=criteria
        )

        return Response(data={"items": data}, status=status.HTTP_200_OK)
