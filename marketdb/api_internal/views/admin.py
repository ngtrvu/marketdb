from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from common.utils.datetime_util import isostring_to_datetime
from core.libs.intraday.intraday_manager import IntradayManager
from api_admin.serializers.stock_price_realtime import (
    StockPriceRealtimeSerializer,
)
from api_admin.views.bank import BankViewSet
from api_admin.views.collection import (
    CollectionGroupViewSet,
    CollectionViewSet,
)
from api_admin.views.crypto import CryptoViewSet
from api_admin.views.etf import ETFViewSet
from api_admin.views.fund import MutualFundViewSet
from api_admin.views.industry import IndustryViewSet
from api_admin.views.stock import StockViewSet
from api_admin.views.stock_event import StockEventViewSet
from core.models.stocks.stock_price_realtime import StockPriceRealtime


class InternalBankViewSet(BankViewSet):
    authentication_classes = []


class InternalCollectionViewSet(CollectionViewSet):
    authentication_classes = []


class InternalCollectionGroupViewSet(CollectionGroupViewSet):
    authentication_classes = []


class InternalCryptoViewSet(CryptoViewSet):
    authentication_classes = []


class InternalMutualFundViewSet(MutualFundViewSet):
    authentication_classes = []


class InternalIndustryViewSet(IndustryViewSet):
    authentication_classes = []


class InternalStockViewSet(StockViewSet):
    authentication_classes = []


class InternalStockPriceRealtimeViewSet(viewsets.ModelViewSet):
    queryset = StockPriceRealtime.objects.all()
    serializer_class = StockPriceRealtimeSerializer
    filter_backends = (
        SearchFilter,
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = {
        "symbol": ["exact", "in"],
        "type": ["exact"],
        "exchange": ["exact"],
    }
    ordering_fields = "__all__"
    ordering = ("-created",)
    search_fields = ["symbol"]
    authentication_classes = []

    def add_price_realtime(self, items):
        intraday_manager = IntradayManager()
        symbols = []
        for item in items:
            symbols.append(item["symbol"])

        prices = intraday_manager.get_prices(symbols=symbols)
        for item in items:
            symbol = item.get("symbol")

            db_price = item.get("price")
            db_timestamp = float(isostring_to_datetime(item["datetime"]).timestamp())

            rd_price = prices.get(symbol, {}).get("price")
            rd_timestamp = prices.get(symbol, {}).get("timestamp")
            if rd_price and rd_timestamp > db_timestamp:
                item["price"] = rd_price
                item["datetime"] = datetime.fromtimestamp(rd_timestamp)

        return items

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = self.add_price_realtime(serializer.data)
        return Response(data=data)


class InternalStockEventViewSet(StockEventViewSet):
    authentication_classes = []
