from datetime import datetime

import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText, FuzzyInteger
from pytz import timezone

from common.utils.datetime_util import VN_TIMEZONE
from core.models.funds.fund import MutualFund
from core.models.funds.fund_nav import MutualFundNavDaily


class MutualFundFactory(DjangoModelFactory):

    class Meta:
        model = MutualFund

    name = FuzzyText(length=50)
    description = FuzzyText(length=500)
    photo = factory.django.ImageField(
        color=factory.fuzzy.FuzzyChoice(['blue', 'yellow', 'green', 'orange']),
        height=100,
        width=100,
    )


class MutualFundNavDailyFactory(DjangoModelFactory):

    class Meta:
        model = MutualFundNavDaily

    datetime = datetime.now(tz=timezone(VN_TIMEZONE))
    nav = FuzzyInteger(10000, 50000)
