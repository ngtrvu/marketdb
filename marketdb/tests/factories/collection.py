from factory.django import DjangoModelFactory

from core.models.screener.collection import Collection, Metric, WatchlistCollection


class CollectionFactory(DjangoModelFactory):

    class Meta:
        model = Collection


class MetricFactory(DjangoModelFactory):

    class Meta:
        model = Metric


class WatchlistCollectionFactory(DjangoModelFactory):

    class Meta:
        model = WatchlistCollection
