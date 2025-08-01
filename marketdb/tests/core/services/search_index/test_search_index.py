from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models.mixin import ContentStatusEnum
from core.models.stocks.stock import Stock
from core.models.etfs.etf import ETF
from core.models.search_index import SearchIndex
from core.services.search.search_index import (
    SearchReindexService,
    generate_search_vector,
)
from tests.factories.stock import StockFactory
from tests.factories.etf import ETFFactory


class SearchIndexTestCase(TestCase):
    def setUp(self):
        super(SearchIndexTestCase, self).setUp()

        self.stock1 = StockFactory(
            symbol="ACB",
            name="Ngan hang co phan A Chau",
            status=ContentStatusEnum.PUBLISHED,
            exchange_status=Stock.STATUS_LISTED,
        )
        self.stock2 = StockFactory(
            symbol="VCB",
            name="Ngan hang vietcombank",
            status=ContentStatusEnum.PUBLISHED,
            exchange_status=Stock.STATUS_LISTED,
        )
        self.stock3 = StockFactory(
            symbol="PIS",
            name="Tổng Công ty Pisico Bình Định - CTCP",
            status=ContentStatusEnum.PUBLISHED,
            exchange_status=Stock.STATUS_LISTED,
        )
        self.stock4 = StockFactory(
            symbol="HPG",
            name="Thep Hoa Phat",
            status=ContentStatusEnum.PUBLISHED,
            exchange_status=Stock.STATUS_LISTED,
        )
        self.stock5 = StockFactory(
            symbol="SPH",
            name="CTCP Xuất nhập khẩu Thủy sản Hà Nội",
            status=ContentStatusEnum.PUBLISHED,
            exchange_status=Stock.STATUS_LISTED,
        )
        self.etf1 = ETFFactory(
            symbol="FUEVFVND",
            name="DC ETF Diamond",
            status=ContentStatusEnum.PUBLISHED,
            exchange_status=ETF.STATUS_LISTED,
        )

    def test_get_search_results_success(self):
        index_count = SearchIndex.objects.count()
        self.assertEqual(index_count, 0)

        service = SearchReindexService()
        success = service.call()
        self.assertEqual(service.get_error_message(), None)
        self.assertTrue(success)

        index_count = SearchIndex.objects.count()
        self.assertEqual(index_count, 6)
