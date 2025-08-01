from datetime import datetime
from pytz import timezone
from factory.django import DjangoModelFactory

from common.utils.datetime_util import VN_TIMEZONE
from factory.fuzzy import FuzzyInteger
from core.models.funds.fund_nav import MutualFundNavIndex


class FundPriceIndexFactory(DjangoModelFactory):

    class Meta:
        model = MutualFundNavIndex

    datetime = datetime.now(tz=timezone(VN_TIMEZONE))
    nav = FuzzyInteger(10000, 100000)
    total_nav = FuzzyInteger(10000, 100000)
