import datetime
from dateutil.relativedelta import relativedelta

DATE_RANGE_1D = "1d"
DATE_RANGE_1W = "1w"
DATE_RANGE_1M = "1m"
DATE_RANGE_3M = "3m"
DATE_RANGE_6M = "6m"
DATE_RANGE_1Y = "1y"
DATE_RANGE_3Y = "3y"
DATE_RANGE_5Y = "5y"
DATE_RANGE_YTD = "ytd"
DATE_RANGES = ["1d", "1w", "1m", "3m", "1y", "5y"]
HISTORICAL_DATE_RANGES = ["1w", "1m", "3m", "1y", "5y"]


def get_range_dates(date_range, to_date=datetime.date.today()):
    date_range = date_range.lower()

    if date_range == DATE_RANGE_1D:
        from_date = to_date - datetime.timedelta(days=1)
    elif date_range == DATE_RANGE_1W:
        from_date = to_date - datetime.timedelta(days=7)
    elif date_range == DATE_RANGE_1M:
        from_date = to_date - relativedelta(months=1)
    elif date_range == DATE_RANGE_3M:
        from_date = to_date - relativedelta(months=3)
    elif date_range == DATE_RANGE_6M:
        from_date = to_date - relativedelta(months=6)
    elif date_range == DATE_RANGE_1Y:
        from_date = to_date - relativedelta(years=1)
    elif date_range == DATE_RANGE_3Y:
        from_date = to_date - relativedelta(years=3)
    elif date_range == DATE_RANGE_5Y:
        from_date = to_date - relativedelta(years=5)
    elif date_range == DATE_RANGE_YTD:
        from_date = to_date.replace(day=1, month=1)
    else:
        return None, None

    from_date_string = from_date.strftime("%Y-%m-%d")
    to_date_string = to_date.strftime("%Y-%m-%d")
    return from_date_string, to_date_string
