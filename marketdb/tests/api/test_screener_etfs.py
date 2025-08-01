from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models.mixin import BaseModel, AssetType
from tests.testutils.apitest import APITest
from tests.factories.etf import ETFFactory
from tests.factories.stock_analytics import StockFAFactory
from tests.factories.stock_price_analytics import StockPriceAnalyticsFactory
from tests.factories.stock_price_realtime import StockPriceRealtimeFactory


class ScreenerETFsApiTestCase(APITest):
    def setUp(self):
        super(ScreenerETFsApiTestCase, self).setUp()

        ETFFactory(symbol="E1VFVN30", name="Quy E1VFVN30", exchange='hose')
        ETFFactory(symbol="FUEVFVND", name="Quy FUEVFVND", exchange='hose')
        ETFFactory(symbol="FUEVN100", name="Quy FUEVN100", exchange='hose')

        StockFAFactory(symbol="E1VFVN30", year=2022, market_cap=1000000000, pe=4)
        StockFAFactory(symbol="FUEVFVND", year=2022, market_cap=900000000, pe=3)
        StockFAFactory(symbol="FUEVN100", year=2022, market_cap=800000000, pe=3.5)

        StockPriceAnalyticsFactory(
            symbol="E1VFVN30", reference=20000, price_1d=20000, volume_1d=1000, fb_volume_1d=1000,
            fs_volume_1d=0,
        )
        StockPriceAnalyticsFactory(
            symbol="FUEVFVND", reference=25000, price_1d=25000, volume_1d=2000, fb_volume_1d=2000,
            fs_volume_1d=0,
        )
        StockPriceAnalyticsFactory(
            symbol="FUEVN100", reference=25000, price_1d=25000, volume_1d=2000, fb_volume_1d=3000,
            fs_volume_1d=0,
        )

        StockPriceRealtimeFactory(
            type=AssetType.ETF, market_cap=1000000000,
            symbol="E1VFVN30", price=22000, volume=1500, open=20000, high=21500, low=19000, close=22000)
        StockPriceRealtimeFactory(
            type=AssetType.ETF, market_cap=900000000,
            symbol="FUEVFVND", price=28000, volume=2500, open=20000, high=32000, low=26000, close=28000)
        StockPriceRealtimeFactory(
            type=AssetType.ETF, market_cap=800000000,
            symbol="FUEVN100", price=27000, volume=5500, open=20000, high=32000, low=26000, close=28000)

        self.client = APIClient()

    def test_get_screener_etfs(self):
        base_url = reverse('api:screener-etfs')
        fields = "symbol,price,volume"
        url = f"{base_url}?fields={fields}&filters=pe__gt__3,market_cap__gte__800000000&sorts=market_cap__asc"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['paging']['count'], 2)
        self.assertEqual(response.data['items'][0]['symbol'], "FUEVN100")
        self.assertEqual(response.data['items'][0]['price'], 27000)
        self.assertEqual(response.data['items'][0]['volume'], 5500)

        self.assertEqual(response.data['items'][1]['symbol'], "E1VFVN30")
        self.assertEqual(response.data['items'][1]['price'], 22000)
        self.assertEqual(response.data['items'][1]['volume'], 1500)
