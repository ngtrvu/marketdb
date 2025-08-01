from common.utils.datetime_util import is_weekend, get_date_str, str_to_datetime, VN_TIMEZONE
from core.services.base import BaseService
from core.models.market.market_calendar import MarketCalendar, MarketStatusEnum


class CheckCalendarService(BaseService):

    def __init__(self, date: str):
        self.date = date
        self.datetime_obj = str_to_datetime(self.date, date_format="%Y-%m-%d", tz=VN_TIMEZONE)

    def is_valid(self) -> bool:
        if not self.datetime_obj:
            self.error_message = "Invalid date format, should be %Y-%m-%d"
            raise Exception(self.error_message)
        return True

    def call(self) -> bool:
        if not self.is_valid():
            return False

        # get the open status from db
        calendar = MarketCalendar.objects.filter(date=self.datetime_obj.date()).first()
        if calendar:
            self.data = calendar
            return calendar.status == MarketStatusEnum.OPEN

        # For most of the cases, we don't have it on the database. Use the default setting, no trading on the weekend
        return not is_weekend(datetime_obj=self.datetime_obj)
