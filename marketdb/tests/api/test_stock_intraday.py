from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.libs.intraday.intraday_manager import IntradayManager
from tests.testutils.apitest import APITest
from tests.factories.stock import StockFactory


class StockIntradayApiTestCase(APITest):
    def setUp(self):
        super(StockIntradayApiTestCase, self).setUp()

        self.stock1 = StockFactory(symbol="ACB", name="Ngan hang A Chau")
        self.stock2 = StockFactory(symbol="VCB", name="Ngan hang vietcombank")

        self.client = APIClient()

    @patch.object(IntradayManager, "get_and_build_chart_intraday")
    @patch.object(IntradayManager, "__init__")
    def test_get_intraday_results_success(self, init, order_stats):
        init.return_value = None
        order_stats.return_value = {"10.0": 100, "12.2": 200, "12.5": 150}

        url = reverse("api:stock-order-stats", args=["ACB"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 3)
        self.assertEqual(response.data["items"][0]["price"], 10.0)
        self.assertEqual(response.data["items"][0]["volume"], 100.0)

    @patch.object(IntradayManager, "get_and_build_chart_intraday")
    @patch.object(IntradayManager, "__init__")
    def test_get_intraday_results_failed(self, init, order_stats):
        init.return_value = None
        order_stats.return_value = {}

        url = reverse("api:stock-order-stats", args=["XYZ"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse("api:stock-order-stats", args=["VCB"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"], [])

    @patch.object(IntradayManager, "get_and_build_chart_intraday")
    @patch.object(IntradayManager, "__init__")
    def test_invalid_operation(self, init, order_stats):
        init.return_value = None

        order_stats.return_value = {
            "10.0": 1234567890_1234567890_1234567890,
            "11.0": 100,
            "22.0": 111_222_333_444,
            "33.0": 555_444_333_222_111_000,
        }
        url = reverse("api:stock-order-stats", args=["ACB"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 3)
        self.assertEqual(response.data["items"][0]["price"], 11.0)
        self.assertEqual(response.data["items"][0]["volume"], 100)
        self.assertEqual(response.data["items"][1]["price"], 22.0)
        self.assertEqual(response.data["items"][1]["volume"], 111_222_333_444.0)
        self.assertEqual(response.data["items"][2]["price"], 33.0)
        self.assertEqual(response.data["items"][2]["volume"], 555_444_333_222_111_000)
        