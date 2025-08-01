from datetime import datetime
from pytz import timezone
from factory.django import DjangoModelFactory

from common.utils.datetime_util import VN_TIMEZONE
from factory.fuzzy import FuzzyInteger, FuzzyDecimal
from core.models.market.market_analytics import FearGreedIndexDaily


class FearGreedIndexFactory(DjangoModelFactory):

    class Meta:
        model = FearGreedIndexDaily

    datetime = datetime.now(tz=timezone(VN_TIMEZONE))
    date = datetime.now(tz=timezone(VN_TIMEZONE)).date()
    score = FuzzyInteger(0, 100)
