from django.test import TestCase

from core.services.fund.get_funds import GetFundsService
from tests.factories.fund import MutualFundFactory
from tests.factories.fund_price_index import FundPriceIndexFactory


class GetFundsServiceTestCase(TestCase):
    def setUp(self):
        MutualFundFactory(symbol="DCDS", name="Quy DCDS")
        MutualFundFactory(symbol="DCBF", name="Quy DCBF")
        MutualFundFactory(symbol="VFF", name="Quy FUEVN100")

        FundPriceIndexFactory(symbol="DCDS", nav=22000, total_nav=1000000000)
        FundPriceIndexFactory(symbol="DCBF", nav=18000, total_nav=800000000)
        FundPriceIndexFactory(symbol="VFF", nav=30000, total_nav=500000000)

        super(GetFundsServiceTestCase, self).setUp()

    def test_get_etfs(self):
        filters = [
            {'name': 'nav', 'operator': 'gte', 'value': 20000},
        ]
        sorts = [
            {'name': 'total_nav', 'type': 'asc'}
        ]
        fields = ['symbol', 'nav', 'total_nav']
        result = GetFundsService(fields=fields, filters=filters, sorts=sorts).call()

        self.assertEqual(result[0].symbol, "VFF")
        self.assertEqual(result[0].nav, 30000)
        self.assertEqual(result[0].total_nav, 500000000)

        self.assertEqual(result[1].symbol, "DCDS")
        self.assertEqual(result[1].nav, 22000)
        self.assertEqual(result[1].total_nav, 1000000000)

        self.assertEqual(len(result), 2)
