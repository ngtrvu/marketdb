from django.urls import reverse
from rest_framework import status

from tests.factories.industry import IndustryFactory
from tests.testutils.apitest import AdminAPITest


class IndexerTestCase(AdminAPITest):

    def test_create_or_update(self):
        url = reverse("api_internal:data-indexer")
        data = {
            "model_name": "StockPriceAnalytics",
            "key_name": "symbol",
            "key_value": "ACB",
            "payload": {"datetime": "2023-07-03 09:50:27.438178+00"},
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        industry = IndustryFactory()
        data = {
            "key_name": "industry_id",
            "key_value": industry.pk,
            "model_name": "IndustryAnalytics",
            "payload": {
                "market_cap": 596724926400,
                "market_cap_1d": 596724926400.0,
                "market_cap_1w": 565859844000.0,
                "market_cap_1m": 479694822300.0,
                "market_cap_3m": 462976236000.0,
                "market_cap_6m": 635306279400.0,
                "market_cap_1y": 228401609760.0,
                "market_cap_3y": 193169118200.4,
                "market_cap_5y": 281474118946.8,
                "market_cap_ytd": 470692506600.0,
                "change_percentage_1d": 0.0,
                "change_percentage_1w": 5.454545454545454,
                "change_percentage_1m": 24.396782841823057,
                "change_percentage_3m": 28.88888888888889,
                "change_percentage_6m": -6.0728744939271255,
                "change_percentage_1y": 161.26126126126127,
                "change_percentage_3y": 208.91321136587575,
                "change_percentage_5y": 111.99992689657694,
                "change_percentage_ytd": 26.775956284153004,
                "icb_code": 9574,
                "datetime": "2024-01-12T08:56:54.154+07:00",
            },
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_or_update_fail(self):
        url = reverse("api_internal:data-indexer")
        data = {
            "model_name": "StockPriceAnalytics",
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "model_name": "dummy",
            "key_name": "symbol",
            "key_value": "ACB",
            "payload": {"datetime": "2023-07-03 09:50:27.438178+00"},
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "model_name": "dummy",
            "key_name": "symbol",
            "key_value": "ACB",
            "payload": {},
        }
        response = self.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
