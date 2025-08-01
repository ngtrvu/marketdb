from django.test import TestCase

from core.services.bank.get_banks import GetBanksService
from tests.factories.bank import BankFactory


class GetBanksServiceTestCase(TestCase):
    def setUp(self):
        BankFactory(
            symbol="ACB", title="Ngan hang A Chau", slug='ngan-hang-acb',
            online_savings_1m=0.05,
            online_savings_3m=0.052,
            online_savings_6m=0.054,
            online_savings_9m=0.056,
            online_savings_12m=0.062,
            online_savings_24m=0.065,
            online_savings_36m=0.07,
        )
        BankFactory(
            symbol="MBB", title="Ngan hang quan doi", slug='ngan-hang-mbb',
            online_savings_1m=0.045,
            online_savings_3m=0.048,
            online_savings_6m=0.050,
            online_savings_9m=0.052,
            online_savings_12m=0.058,
            online_savings_24m=0.06,
            online_savings_36m=0.062,
        )
        BankFactory(
            symbol="VCB", title="Ngan hang VCB", slug='ngan-hang-vcb',
            online_savings_1m=0.040,
            online_savings_3m=0.042,
            online_savings_6m=0.046,
            online_savings_9m=0.050,
            online_savings_12m=0.054,
            online_savings_24m=0.058,
            online_savings_36m=0.06,
        )
        BankFactory(
            symbol="VPB", title="Ngan hang VPB", slug='ngan-hang-vpb',
            online_savings_1m=0.044,
            online_savings_3m=0.046,
            online_savings_6m=0.05,
            online_savings_9m=0.055,
            online_savings_12m=0.06,
            online_savings_24m=0.062,
            online_savings_36m=0.066,
        )

        super(GetBanksServiceTestCase, self).setUp()

    def test_get_banks(self):
        filters = [
            {'name': 'online_savings_12m', 'operator': 'gte', 'value': 0.055},
        ]
        sorts = [
            {'name': 'online_savings_12m', 'type': 'desc'}
        ]
        fields = ['symbol', 'title', 'online_savings_6m', 'online_savings_12m']
        result = GetBanksService(fields=fields, filters=filters, sorts=sorts).call()

        self.assertEqual(result[0].symbol, "ACB")
        self.assertEqual(result[0].title, "Ngan hang A Chau")
        self.assertEqual(float(result[0].online_savings_6m), 0.054)
        self.assertEqual(float(result[0].online_savings_12m), 0.062)

        self.assertEqual(result[1].symbol, "VPB")
        self.assertEqual(result[1].title, "Ngan hang VPB")
        self.assertEqual(float(result[1].online_savings_6m), 0.05)
        self.assertEqual(float(result[1].online_savings_12m), 0.06)

        self.assertEqual(result[2].symbol, "MBB")
        self.assertEqual(result[2].title, "Ngan hang quan doi")
        self.assertEqual(float(result[2].online_savings_6m), 0.05)
        self.assertEqual(float(result[2].online_savings_12m), 0.058)

        self.assertEqual(len(result), 3)
