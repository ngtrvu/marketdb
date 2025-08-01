from django.test import TestCase

from core.services.bank.get_banks_savings import GetBanksSavingsService
from tests.factories.bank import BankFactory


class GetBanksSavingsServiceTestCase(TestCase):
    def setUp(self):
        self.bank_acb = BankFactory(
            symbol="ACB", title="Ngan hang A Chau", slug='ngan-hang-acb',
            online_savings_1m=0.05,
            online_savings_3m=0.052,
            online_savings_6m=0.054,
            online_savings_9m=0.056,
            online_savings_12m=0.062,
            online_savings_24m=0.065,
            online_savings_36m=0.07,
        )
        self.bank_mbb = BankFactory(
            symbol="MBB", title="Ngan hang quan doi", slug='ngan-hang-mbb',
            online_savings_1m=0.045,
            online_savings_3m=0.048,
            online_savings_6m=0.050,
            online_savings_9m=0.052,
            online_savings_12m=0.058,
            online_savings_24m=0.06,
            online_savings_36m=0.062,
        )
        self.bank_vcb = BankFactory(
            symbol="VCB", title="Ngan hang VCB", slug='ngan-hang-vcb',
            online_savings_1m=0.040,
            online_savings_3m=0.042,
            online_savings_6m=0.046,
            online_savings_9m=None,
            online_savings_12m=0.054,
            online_savings_24m=0.058,
            online_savings_36m=0.06,
        )
        self.bank_vpb = BankFactory(
            symbol="VPB", title="Ngan hang VPB", slug='ngan-hang-vpb',
            online_savings_1m=0.044,
            online_savings_3m=0.046,
            online_savings_6m=0.05,
            online_savings_9m=0.055,
            online_savings_12m=0.06,
            online_savings_24m=0.062,
            online_savings_36m=0.066,
        )

        super(GetBanksSavingsServiceTestCase, self).setUp()

    def test_savings_bank_calculate(self):
        savings_amount = 100000000
        savings_time = "online_savings_9m"

        service = GetBanksSavingsService(savings_amount=savings_amount, savings_time=savings_time, limit=10)
        queryset = service.call()

        self.assertEqual(queryset[0].symbol, "ACB")
        self.assertEqual(queryset[0].profit, savings_amount * self.bank_acb.online_savings_9m * 9 / 12)
        self.assertEqual(queryset[0].total, savings_amount + savings_amount * self.bank_acb.online_savings_9m * 9 / 12)
        self.assertEqual(queryset[0].savings_amount, savings_amount)
        self.assertEqual(float(queryset[0].savings_percentage), float(self.bank_acb.online_savings_9m))

        self.assertEqual(queryset[1].symbol, "VPB")

        self.assertEqual(queryset[2].symbol, "MBB")

        self.assertEqual(queryset[3].symbol, "VCB")
        self.assertEqual(queryset[3].profit, None)
        self.assertEqual(queryset[3].total, None)
        self.assertEqual(queryset[3].savings_amount, savings_amount)
        self.assertEqual(queryset[3].savings_percentage, None)

        # Limit 2
        service = GetBanksSavingsService(savings_amount=savings_amount, savings_time=savings_time, limit=2)
        queryset = service.call()

        self.assertEqual(queryset.count(), 2)
