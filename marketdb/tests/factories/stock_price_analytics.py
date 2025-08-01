from datetime import datetime
from pytz import timezone
from factory.django import DjangoModelFactory

from common.utils.datetime_util import VN_TIMEZONE
from core.models.stocks.stock_price_analytics import StockPriceAnalytics


class StockPriceAnalyticsFactory(DjangoModelFactory):

    class Meta:
        model = StockPriceAnalytics

    date = datetime.now(tz=timezone(VN_TIMEZONE)).date()
    datetime = datetime.now(tz=timezone(VN_TIMEZONE))
