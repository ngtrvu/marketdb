import pytz
from datetime import datetime, timedelta

from django.utils import timezone
from django.conf import settings


class LocalTimeService:

    def get_begin_today(self) -> datetime:
        tz = pytz.timezone(settings.APP_TIME_ZONE)
        result = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        return result

    def get_now(self) -> datetime:
        tz = pytz.timezone(settings.APP_TIME_ZONE)
        return datetime.now(tz)

    def convert_to_local_datetime(self, dt_value: datetime) -> datetime:
        tz = pytz.timezone(settings.APP_TIME_ZONE)
        local_dt = timezone.localtime(dt_value, tz)
        return local_dt

    def get_timerange_for_24_hours(self):
        from_time = self.get_begin_today()
        to_time = from_time + timedelta(days=1)
        return from_time, to_time

    def validate_date_format(self, date_text, format='%Y-%m-%d'):
        try:
            datetime.strptime(date_text, format)
            return True
        except ValueError:
            # raise ValueError(f"Incorrect data format, should be {f}")
            pass
        return False

    def time_in_range(self, start, end, x):
        """Return true if x is in the range [start, end]"""
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end
