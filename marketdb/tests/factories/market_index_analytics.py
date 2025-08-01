from factory.django import DjangoModelFactory

from common.utils.datetime_util import get_datetime_now, VN_TIMEZONE
from core.models.market_index.market_index_analytics import MarketIndexAnalytics


class MarketIndexAnalyticsFactory(DjangoModelFactory):

    class Meta:
        model = MarketIndexAnalytics
