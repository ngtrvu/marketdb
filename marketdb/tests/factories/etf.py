import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from core.models.etfs.etf import ETF


class ETFFactory(DjangoModelFactory):

    class Meta:
        model = ETF

    name = FuzzyText(length=50)
    description = FuzzyText(length=500)
    photo = factory.django.ImageField(
        color=factory.fuzzy.FuzzyChoice(['blue', 'yellow', 'green', 'orange']),
        height=100,
        width=100,
    )
    exchange = FuzzyText(length=3)
