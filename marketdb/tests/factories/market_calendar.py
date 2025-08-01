import factory
from factory.django import DjangoModelFactory

from core.models.market.market_calendar import MarketCalendar


class MarketCalendarFactory(DjangoModelFactory):

    class Meta:
        model = MarketCalendar
