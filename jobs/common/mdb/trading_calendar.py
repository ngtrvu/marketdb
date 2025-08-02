from datetime import timedelta

from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
)
from common.mdb.client import MarketdbClient


class TradingCalendar(object):

    def is_trading_date(self, input_date: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

    def get_yesterday_str(self, input_date: str) -> str:
        datetime_obj = str_to_datetime(
            input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return get_date_str(
            datetime_obj - timedelta(days=1), date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

    def get_previous_trading_date(self, input_date: str) -> str:
        """Get the most recent previous trading date."""
        most_recent_trading_date = self.get_yesterday_str(input_date=input_date)

        while not self.is_trading_date(input_date=most_recent_trading_date):
            most_recent_trading_date = self.get_yesterday_str(
                input_date=most_recent_trading_date
            )

        return most_recent_trading_date
