import decimal
from datetime import datetime

from common.utils.datetime_util import ensure_tzaware_datetime

from core.services.base import BaseService
from core.libs.intraday.intraday_manager import IntradayManager
from core.models.stocks.stock_price_realtime import StockPriceRealtime


class GetStockPriceRealTimeService(BaseService):

    def __init__(self, symbol):
        self.symbol = symbol
        self.instance = StockPriceRealtime.objects.filter(symbol=self.symbol).first()

    def is_valid(self) -> bool:
        if not self.instance:
            self.error_message = f"Stock {self.symbol} is not exists"
            return False

        return True

    def call(self):
        if not self.is_valid():
            return None

        intraday_manager = IntradayManager()
        intraday_price, intraday_timestamp = intraday_manager.get_price(symbol=self.instance.symbol)
        if intraday_price and intraday_timestamp:
            intraday_datetime = ensure_tzaware_datetime(datetime.fromtimestamp(int(intraday_timestamp)))

            # cache is fresher
            if self.instance.datetime < intraday_datetime:
                self.instance.datetime = intraday_datetime
                self.instance.price = decimal.Decimal(intraday_price)

        return self.instance
