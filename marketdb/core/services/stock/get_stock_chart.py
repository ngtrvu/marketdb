import decimal
import time

from core.services.base import BaseService
from core.models.stocks.stock_price_chart import StockPriceChart
from core.models.stocks.stock_price_realtime import StockPriceRealtime


class GetStockChartService(BaseService):

    change_value = None
    change_percentage = None
    movement = []
    datetime = None

    def __init__(self, symbol, date_range=None):
        self.price = None
        self.symbol = symbol
        self.date_range = date_range

    def is_valid(self) -> bool:
        if self.date_range not in ['1w', '1m', '3m', '6m', '1y', '3y', '5y', 'ytd', 'all']:
            self.error_message = "Range is not supported"
            return False

        return True

    def calculate_change(self, init_value, current_value):
        change_val = current_value - init_value
        change_pct = change_val / current_value * decimal.Decimal(100)
        return change_val, change_pct

    def call(self):
        if not self.is_valid():
            return False

        chart = StockPriceChart.objects.get(symbol=self.symbol)

        try:
            realtime = StockPriceRealtime.objects.get(symbol=self.symbol)
        except Exception as e:
            self.error_message = f"{e}"
            return False

        if not chart or not realtime:
            return False

        movement = self.get_chart_movement(chart)
        latest_avt = {
            "a": realtime.price,
            "v": realtime.volume,
            "t": time.mktime(realtime.datetime.timetuple()),
        }

        if movement:
            movement.append(latest_avt)
        else:
            movement = []

        self.data = chart
        self.price = realtime.price
        self.movement = movement
        self.datetime = chart.datetime

        return True

    def get_chart_movement(self, obj):
        if self.date_range == '1w':
            return obj.movement_1w
        elif self.date_range == '1m':
            return obj.movement_1m
        elif self.date_range == '3m':
            return obj.movement_3m
        elif self.date_range == '6m':
            return obj.movement_6m
        elif self.date_range == '1y':
            return obj.movement_1y
        elif self.date_range == '3y':
            return obj.movement_3y
        elif self.date_range == '5y':
            return obj.movement_5y
        elif self.date_range == 'ytd':
            return obj.movement_ytd
        elif self.date_range == 'all':
            if obj.movement_5y:
                return obj.movement_5y
            elif obj.movement_3y:
                return obj.movement_3y
            elif obj.movement_1y:
                return obj.movement_1y

        return []
