import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from core.models.bank import Bank


class BankFactory(DjangoModelFactory):

    class Meta:
        model = Bank

    title = FuzzyText(length=50)
    slug = FuzzyText(length=50)
    photo = factory.django.ImageField(
        color=factory.fuzzy.FuzzyChoice(['blue', 'yellow', 'green', 'orange']),
        height=100,
        width=100,
    )
