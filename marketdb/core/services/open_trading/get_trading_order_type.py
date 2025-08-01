from common.utils.datetime_util import get_datetime_now, VN_TIMEZONE

from core.services.base import BaseService
from core.services.open_trading.check_calendar import CheckCalendarService


DEFAULT_SYMBOL = 'ACB'


class GetTradingOrderTypeService(BaseService):

    def __init__(self, symbol: str):
        self.symbol = symbol

    def is_valid(self) -> bool:
        return True

    def format_data(self, lo=True, mp=False, ato=False, atc=False):
        return [
            {'label': 'Lệnh giới hạn (LO)', 'type': 'lo', 'is_active': lo},
            {'label': 'Lệnh MP', 'type': 'mp', 'is_active': mp},
            {'label': 'Lệnh ATO', 'type': 'ato', 'is_active': ato},
            {'label': 'Lệnh ATC', 'type': 'atc', 'is_active': atc},
        ]

    def call(self) -> list:
        if not self.is_valid():
            return []

        datetime_obj = get_datetime_now(tz=VN_TIMEZONE)
        date_str = datetime_obj.strftime('%Y-%m-%d')
        is_trading_date = CheckCalendarService(date=date_str).call()
        if not is_trading_date:
            return self.format_data()

        today_0900 = datetime_obj.replace(hour=9, minute=0, second=0)
        today_0915 = datetime_obj.replace(hour=9, minute=15, second=0)
        today_1130 = datetime_obj.replace(hour=11, minute=30, second=0)
        today_1300 = datetime_obj.replace(hour=13, minute=0, second=0)
        today_1430 = datetime_obj.replace(hour=14, minute=30, second=0)
        today_1445 = datetime_obj.replace(hour=14, minute=45, second=0)
        today_1600 = datetime_obj.replace(hour=16, minute=0, second=0)

        if datetime_obj < today_0900 or datetime_obj >= today_1600:
            return self.format_data(lo=True, ato=True, atc=True)
        elif today_0900 <= datetime_obj < today_0915:
            return self.format_data(lo=True, ato=True)
        elif today_0915 <= datetime_obj < today_1430:
            return self.format_data(lo=True, ato=False, mp=True, atc=True)
        elif today_1430 <= datetime_obj < today_1445:
            return self.format_data(lo=True, atc=True)
        elif today_1445 <= datetime_obj < today_1600:
            # show LO but matching depend on stagedu
            return self.format_data(lo=True, ato=False, mp=False, atc=False)

        return self.format_data(lo=True)
