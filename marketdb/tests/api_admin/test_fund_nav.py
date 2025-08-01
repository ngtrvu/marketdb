from datetime import datetime
from decimal import Decimal

from dateutil.tz import tzoffset
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.fund import MutualFund, MutualFundNavDailyFactory
from tests.factories.fund_price_analytics import FundPriceAnalyticsFactory
from tests.factories.fund_price_index import FundPriceIndexFactory
from tests.testutils.apitest import AdminAPITest


class FundPriceAnalyticsApiAdminTestCase(AdminAPITest):
    def setUp(self):
        super(FundPriceAnalyticsApiAdminTestCase, self).setUp()

        self.fund1 = MutualFund(symbol="VCAMBF", name="VCAMBF")
        self.fund2 = MutualFund(symbol="VSAF", name="VSAF")

        FundPriceIndexFactory(symbol="VCAMBF", nav=15000, total_nav=15000 * 10000000)
        FundPriceIndexFactory(symbol="VSAF", nav=25000, total_nav=25000 * 10000000)

        stock_datetime = datetime(2023, 8, 8, 8, 8, 8, tzinfo=tzoffset(None, 25200))

        nav_daily = MutualFundNavDailyFactory(
            symbol="VCAMBF",
            nav=14000.0,
            date=datetime(2023, 8, 7, 8, 8, 8, tzinfo=tzoffset(None, 25200)),
            datetime=stock_datetime,
        )
        nav_daily = MutualFundNavDailyFactory(
            symbol="VCAMBF",
            nav=15000.0,
            date=datetime(2023, 8, 8, 8, 8, 8, tzinfo=tzoffset(None, 25200)),
            datetime=stock_datetime,
        )

        self.fund_price_1 = FundPriceAnalyticsFactory(
            symbol="VCAMBF", nav=15000.0, date=stock_datetime, datetime=stock_datetime,
            annualized_return_percentage=Decimal('13.04'), annualized_return_n_year=3,
            maximum_drawdown_percentage=Decimal('49.0')
        )
        self.fund_price_2 = FundPriceAnalyticsFactory(
            symbol="VSAF", nav=25000.0, date=stock_datetime, datetime=stock_datetime
        )

        self.client = APIClient()

    def test_get_admin_fund_detail_success(self):
        url = reverse("api_admin:mutual-fund-price-detail", args=["VCAMBF"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"], "VCAMBF")
        self.assertEqual(response.data["nav"], 15000.0)
        self.assertEqual(response.data["annualized_return_percentage"], Decimal('13.04'))
        self.assertEqual(response.data["annualized_return_n_year"], 3)
        self.assertEqual(response.data["maximum_drawdown_percentage"], Decimal('49.0'))

    def test_get_admin_fund_detail_have_no_performance(self):
        url = reverse("api_admin:mutual-fund-price-detail", args=["VSAF"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"], "VSAF")
        self.assertEqual(response.data["nav"], 25000.0)
        self.assertEqual(response.data["annualized_return_percentage"], None)
        self.assertEqual(response.data["annualized_return_n_year"], None)
        self.assertEqual(response.data["maximum_drawdown_percentage"], None)
