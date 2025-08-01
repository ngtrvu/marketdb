from factory.django import DjangoModelFactory

from core.models.stocks.stock_event import StockEvent


class StockEventFactory(DjangoModelFactory):

    class Meta:
        model = StockEvent
