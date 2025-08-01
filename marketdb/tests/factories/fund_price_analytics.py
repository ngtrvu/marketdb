from datetime import datetime

from factory.fuzzy import FuzzyInteger
from pytz import timezone
from factory.django import DjangoModelFactory

from common.utils.datetime_util import VN_TIMEZONE
from core.models.funds.fund_price_analytics import FundNavAnalytics


class FundPriceAnalyticsFactory(DjangoModelFactory):

    class Meta:
        model = FundNavAnalytics

    datetime = datetime.now(tz=timezone(VN_TIMEZONE))
    nav = FuzzyInteger(10000, 50000)