from factory.django import DjangoModelFactory

from core.models.market_index.market_index import MarketIndex


class MarketIndexFactory(DjangoModelFactory):

    class Meta:
        model = MarketIndex
