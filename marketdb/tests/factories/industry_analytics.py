from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from common.utils.datetime_util import get_datetime_now, VN_TIMEZONE
from core.models.industries.industry_analytics import IndustryAnalytics


class IndustryAnalyticsFactory(DjangoModelFactory):

    class Meta:
        model = IndustryAnalytics

    icb_code = FuzzyInteger(1000, 9999)
    datetime = get_datetime_now(tz=VN_TIMEZONE)
