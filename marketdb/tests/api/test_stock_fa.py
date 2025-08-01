import datetime
from unittest.mock import patch
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient

from core.models.mixin import ContentStatusEnum
from core.models.stocks.stock import Stock
from core.models.stocks.stock_analytics import StockFA
from tests.factories.stock import StockFactory
from tests.factories.stock_analytics import StockFAFactory
from tests.testutils.apitest import APITest


class StockFAApiTestCase(APITest):
    def setUp(self):
        super(StockFAApiTestCase, self).setUp()

        self.stock1 = StockFactory(symbol="HPG", name="Khong Hoa thi Phat", status=ContentStatusEnum.PUBLISHED,
                                   exchange_status=Stock.STATUS_LISTED)
        self.stock2 = StockFactory(symbol="VCB", name="Ngan hang vietcombank", status=ContentStatusEnum.PUBLISHED,
                                   exchange_status=Stock.STATUS_LISTED)
        self.stock3 = StockFactory(symbol="VNM", name="Vinamilk", status=ContentStatusEnum.PUBLISHED,
                                   exchange_status=Stock.STATUS_LISTED)
        self.stock4 = StockFactory(symbol="VNZ", name="Vinagame",
                                   status=ContentStatusEnum.PUBLISHED,
                                   exchange_status=Stock.STATUS_LISTED)

        self.stock1_fa = StockFAFactory(
            symbol=self.stock1.symbol, year=2022, pe=88, eps=4900, date=now().date())
        self.stock3_fa = StockFAFactory(
            symbol=self.stock3.symbol, year=2022, pe=99, eps=5000, date=now().date() - datetime.timedelta(days=1))

        self.client = APIClient()

    def test_get_stock_fa_results_success(self):
        url = reverse('api:stock-fundamental', args=['HPG'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 20)
        self.assertEqual(response.data["items"][0]['label'], 'Mã Cổ Phiếu')
        self.assertIsNotNone(response.data["items"][0]['key'])
        self.assertIsNotNone(response.data["items"][0]['value'])

    def test_get_stock_fa_results_failed(self):
        url = reverse('api:stock-fundamental', args=['VCB'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(response.data)

    def test_get_stock_fa_results_outdate(self):
        url = reverse('api:stock-fundamental', args=['VNM'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data['items']), 2)

    def test_get_stock_fa_results_not_found(self):
        url = reverse('api:stock-fundamental', args=['XYZ'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsNotNone(response.data)
