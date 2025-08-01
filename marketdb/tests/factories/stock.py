import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from core.models.mixin import ContentStatusEnum
from core.models.stocks.stock import Stock


class StockFactory(DjangoModelFactory):

    class Meta:
        model = Stock

    name = FuzzyText(length=50)
    description = FuzzyText(length=500)
    photo = factory.django.ImageField(
        color=factory.fuzzy.FuzzyChoice(['blue', 'yellow', 'green', 'orange']),
        height=100,
        width=100,
    )
    exchange = FuzzyText(length=3)
    status = ContentStatusEnum.PUBLISHED
