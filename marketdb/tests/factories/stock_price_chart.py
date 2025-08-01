from datetime import datetime
from pytz import timezone
from factory.django import DjangoModelFactory

from common.utils.datetime_util import VN_TIMEZONE
from core.models.stocks.stock_price_chart import StockPriceChart


class StockPriceChartFactory(DjangoModelFactory):

    class Meta:
        model = StockPriceChart

    datetime = datetime.now(tz=timezone(VN_TIMEZONE))
