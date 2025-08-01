import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from common.utils.datetime_util import get_date_str


class DateRangeUtils:
    # List Date Range
    DATE_RANGE_1D = '1d'
    DATE_RANGE_3D = '3d'
    DATE_RANGE_1W = '1w'
    DATE_RANGE_1M = '1m'
    DATE_RANGE_3M = '3m'
    DATE_RANGE_6M = '6m'
    DATE_RANGE_1Y = '1y'
    DATE_RANGE_3Y = '3y'
    DATE_RANGE_5Y = '5y'
    DATE_RANGE_YTD = 'ytd'
    DATE_RANGE_ALL = 'all'
    DATE_RANGE_DAYS = 'range_days'

    def get_default_date_ranges(self):
        return [
            self.DATE_RANGE_1D, self.DATE_RANGE_1W,
            self.DATE_RANGE_1M,
            self.DATE_RANGE_3M, self.DATE_RANGE_6M,
            self.DATE_RANGE_1Y,
            self.DATE_RANGE_3Y, self.DATE_RANGE_5Y
        ]

    def validate(self, date_range):
        date_range = date_range.lower()
        if date_range in [
            self.DATE_RANGE_1D, self.DATE_RANGE_3D, self.DATE_RANGE_1W,
            self.DATE_RANGE_1M, self.DATE_RANGE_3M, self.DATE_RANGE_6M,
            self.DATE_RANGE_1Y, self.DATE_RANGE_3Y, self.DATE_RANGE_5Y,
            self.DATE_RANGE_ALL,
        ]:
            return True

        return False

    def get_date_range(self, date_range: str, to_date: datetime.date = datetime.date.today(), delta_days: int = 0):
        date_range = date_range.lower()

        if date_range == self.DATE_RANGE_1D:
            from_date = to_date - relativedelta(days=1)
        elif date_range == self.DATE_RANGE_3D:
            from_date = to_date - relativedelta(days=3)
        elif date_range == self.DATE_RANGE_1W:
            from_date = to_date - relativedelta(weeks=1)
        elif date_range == self.DATE_RANGE_1M:
            from_date = to_date - relativedelta(months=1)
        elif date_range == self.DATE_RANGE_3M:
            from_date = to_date - relativedelta(months=3)
        elif date_range == self.DATE_RANGE_6M:
            from_date = to_date - relativedelta(months=6)
        elif date_range == self.DATE_RANGE_1Y:
            from_date = to_date - relativedelta(years=1)
        elif date_range == self.DATE_RANGE_3Y:
            from_date = to_date - relativedelta(years=3)
        elif date_range == self.DATE_RANGE_5Y:
            from_date = to_date - relativedelta(years=5)
        elif date_range == self.DATE_RANGE_YTD:
            from_date = to_date.replace(month=1, day=1)
        elif date_range == self.DATE_RANGE_ALL:
            from_date = datetime.date(1970, 1, 1)
        elif date_range == self.DATE_RANGE_DAYS and delta_days > 0:
            from_date = to_date - relativedelta(days=delta_days)
        else:
            return None, None

        return from_date, to_date

    def get_date_range_as_string(self, date_range, to_date=datetime.date.today(), date_format: str = "%Y-%m-%d",
                                 tz: str = "UTC"):
        from_date, to_date = self.get_date_range(date_range, to_date)
        from_date_string = get_date_str(from_date, date_format=date_format, tz=tz)
        to_date_string = get_date_str(to_date, date_format=date_format, tz=tz)
        return from_date_string, to_date_string

    def get_dates_by_range(self, from_date: datetime.datetime, to_date: datetime.datetime, date_format: str = None,
                           tz: str = "UTC"):
        delta = to_date - from_date
        if not delta.days:
            raise Exception(f"Invalid given start, end date: {from_date}, {to_date}")

        dates = []
        for i in range(delta.days + 1):
            datetime_obj = from_date + timedelta(days=i)
            if date_format:
                dates.append(get_date_str(datetime_obj, date_format=date_format, tz=tz))
            else:
                dates.append(datetime_obj)

        return dates
