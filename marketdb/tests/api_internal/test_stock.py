from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.stock import StockFactory
from tests.testutils.apitest import APITest


class StockApiInternalTestCase(APITest):
    def setUp(self):
        super(StockApiInternalTestCase, self).setUp()

        self.stock1 = StockFactory(symbol="VCB", name="Ngan hang vietcombank")
        self.stock2 = StockFactory(symbol="ACB", name="Ngan hang A Chau")

        self.client = APIClient()

    def test_get_internal_stock_list_success(self):
        url = reverse("api_internal:stock-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['symbol'], self.stock2.symbol)
        self.assertEqual(response.data[1]['symbol'], self.stock1.symbol)

    def test_get_internal_stock_detail_success(self):
        url = reverse("api_internal:stock-detail", args=[self.stock2.symbol])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"], "ACB")

    def test_get_internal_stock_detail_have_no_data(self):
        url = reverse("api_internal:stock-detail", args=["HPG"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
