from datetime import datetime
from pytz import timezone
from factory.django import DjangoModelFactory

from common.utils.datetime_util import VN_TIMEZONE
from core.models.stocks.stock_analytics import StockFA


class StockFAFactory(DjangoModelFactory):

    class Meta:
        model = StockFA

    datetime = datetime.now(tz=timezone(VN_TIMEZONE))
