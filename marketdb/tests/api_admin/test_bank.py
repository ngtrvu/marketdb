from django.urls import reverse
from rest_framework import status

from tests.testutils.apitest import AdminAPITest
from core.models.bank import Bank
from tests.factories.bank import BankFactory


class BankTestCase(AdminAPITest):
    def setUp(self):
        super(BankTestCase, self).setUp()

        self.bank1 = BankFactory(title='Ngan Hang VCB', symbol='VCB', slug='vcb')
        self.bank2 = BankFactory(title='Ngan Hang MBB', symbol='MBB', slug='mbb')

    def test_get_banks(self):
        url = reverse('api_admin:bank-list')
        response = self.get(url)
        self.assertEqual(response.data['paging']['count'], 2)
        self.assertEqual(response.data['items'][0]['title'], 'Ngan Hang MBB')
        self.assertEqual(response.data['items'][1]['title'], 'Ngan Hang VCB')

    def test_get_bank(self):
        url = reverse('api_admin:bank-detail', args=[self.bank1.pk])

        response = self.get(url)
        self.assertIsNotNone(response.data['title'])

    def test_create_bank(self):
        url = reverse('api_admin:bank-list')
        response = self.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'title': 'Ngan Hang ACB',
            'slug': 'acb',
            'symbol': 'ACB',
            'photo': self.generate_photo_file(),
            'savings_on_demand': 0.05,
            'savings_1m': 0.04,
            'savings_3m': 0.05,
            'savings_6m': 0.052,
            'savings_9m': 0.055,
            'savings_12m': 0.060,
        }

        response = self.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        count = Bank.objects.all().count()
        self.assertEqual(count, 3)

        bank = Bank.objects.filter(symbol='ACB').first()
        self.assertEqual(bank.title, 'Ngan Hang ACB')
        self.assertEqual(float(bank.savings_1m), 0.04)
        self.assertEqual(float(bank.savings_6m), 0.052)
        self.assertEqual(float(bank.savings_9m), 0.055)
        self.assertEqual(float(bank.savings_12m), 0.060)

    def test_update_bank(self):
        data = {
            'title': 'Ngan Hang CP VCB',
        }
        url = reverse('api_admin:bank-detail', args=[self.bank1.pk])
        response = self.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['title'], 'Ngan Hang CP VCB')

    def test_delete_bank(self):
        url = reverse('api_admin:bank-detail', args=[self.bank1.pk])
        response = self.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        count = Bank.objects.all().count()
        self.assertEqual(count, 1)
