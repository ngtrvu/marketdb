import calendar
from datetime import date, datetime, timedelta
from typing import Optional

import pytz
from dateutil import parser
from pytz import timezone

VN_TIMEZONE = "Asia/Ho_Chi_Minh"
UTC_TIMEZONE = "UTC"


def get_date_str(datetime_value: datetime = None, date_format="%Y%m%d", tz=UTC_TIMEZONE) -> str:
    if datetime_value:
        return datetime_value.strftime(date_format)
    return datetime.now(tz=timezone(tz)).strftime(date_format)


def get_gcs_date_format(date_format="%Y/%m/%d", tz=UTC_TIMEZONE) -> str:
    return datetime.now(tz=timezone(tz)).strftime(date_format)


def get_current_time(time_format="%H:%M:%S", tz=UTC_TIMEZONE) -> str:
    return datetime.now(tz=timezone(tz)).strftime(time_format)


def get_current_datetime(format_time="%Y-%m-%d %H:%M:%S%z", tz=UTC_TIMEZONE) -> str:
    return datetime.now(tz=timezone(tz)).strftime(format_time)


def get_datetime_now(tz=UTC_TIMEZONE) -> datetime:
    return datetime.now(tz=timezone(tz))


def is_tzaware(datetime_obj):
    if datetime_obj.tzinfo is not None and datetime_obj.tzinfo.utcoffset(datetime_obj) is not None:
        return True
    return False


def ensure_tzaware_datetime(datetime_obj, tz=UTC_TIMEZONE):
    # skip it if it's timezone aware already
    if is_tzaware(datetime_obj):
        return datetime_obj

    tz = pytz.timezone(tz)
    return tz.localize(datetime_obj)


def set_tzaware_datetime(datetime_obj, tz=UTC_TIMEZONE):
    return datetime_obj.replace(tzinfo=timezone(tz))


def get_now_unix_timestamp(datetime_obj: datetime = None, tz=UTC_TIMEZONE) -> float:
    if not datetime_obj:
        datetime_obj = datetime.now(tz=timezone(tz))
    unix_time = calendar.timegm(datetime_obj.utctimetuple())
    return unix_time


def get_datetime_from_timestamp(timestamp: float, tz=UTC_TIMEZONE) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone(tz))


def replace_tz(datetime_obj: datetime, tz=UTC_TIMEZONE) -> datetime:
    if not datetime_obj:
        return
    tz = pytz.timezone(tz)
    return tz.localize(datetime_obj)


def get_delta_unix_timestamp(n_days: int, tz=UTC_TIMEZONE) -> float:
    d = datetime.now(tz=timezone(tz)) - timedelta(days=n_days)
    unix_time = calendar.timegm(d.utctimetuple())
    return unix_time


def str_to_datetime(input_str: str, date_format: str = "%Y-%m-%d", tz="UTC"):
    if not input_str:
        return

    try:
        datetime_obj = datetime.strptime(input_str, date_format)
    except ValueError:
        return

    if tz:
        tz_obj = timezone(tz)
        datetime_obj = tz_obj.localize(datetime_obj)

    return datetime_obj


def isostring_to_datetime(iso_datetime_str) -> Optional[datetime]:
    if not iso_datetime_str:
        return None

    return parser.parse(iso_datetime_str)


def get_today_date(tz="UTC") -> date:
    tz_obj = timezone(tz)
    return datetime.now(tz_obj).date()


def date_str_reformat(input_date_str: str, to_date_format: str, date_format: str, tz=UTC_TIMEZONE):
    datetime_obj = str_to_datetime(input_date_str, date_format=date_format, tz=tz)
    return get_date_str(datetime_value=datetime_obj, date_format=to_date_format)


def check_time_in_range(start: datetime.time, end: datetime.time, time_obj: datetime.time):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= time_obj <= end
    else:
        return start <= time_obj or time_obj <= end


def is_weekend(datetime_obj: datetime) -> bool:
    week_no = datetime_obj.weekday()
    return week_no > 4


def get_previous_date_str(
    input_date: str, date_format: str = "%Y/%m/%d", tz=UTC_TIMEZONE, n_day=1
) -> str:
    datetime_obj = str_to_datetime(input_date, date_format=date_format, tz=tz)
    return get_date_str(datetime_obj - timedelta(n_day), date_format=date_format, tz=tz)


def before_datetime(datetime_obj: datetime, now: datetime = None) -> bool:
    """Return true if datetime_obj is before now or given datetime"""
    if not now:
        now = get_datetime_now()
    return ensure_tzaware_datetime(datetime_obj) < now


def after_datetime(datetime_obj: datetime, now: datetime = None) -> bool:
    """Return true if datetime_obj is after now or given datetime"""
    if not now:
        now = get_datetime_now()
    return ensure_tzaware_datetime(datetime_obj) > now
