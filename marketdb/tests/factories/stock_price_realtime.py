from datetime import datetime
from pytz import timezone
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from common.utils.datetime_util import VN_TIMEZONE
from core.models.stocks.stock_price_realtime import StockPriceRealtime


class StockPriceRealtimeFactory(DjangoModelFactory):
    class Meta:
        model = StockPriceRealtime

    datetime = datetime.now(tz=timezone(VN_TIMEZONE))
    price = FuzzyInteger(10000, 100000)
