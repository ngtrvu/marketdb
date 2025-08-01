import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from core.models.industries.industry import Industry


class IndustryFactory(DjangoModelFactory):

    class Meta:
        model = Industry

    level = FuzzyInteger(1, 5)
    icb_code = FuzzyInteger(1000, 9999)
