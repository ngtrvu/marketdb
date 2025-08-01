from django.urls import reverse
from rest_framework import status

from tests.testutils.apitest import AdminAPITest
from core.models.stocks.stock import Stock
from tests.factories.stock import StockFactory


class StockTestCase(AdminAPITest):
    def setUp(self):
        super(StockTestCase, self).setUp()

        self.stock1 = StockFactory(name='Ngan Hang VCB', symbol='VCB')
        self.stock2 = StockFactory(name='HPG', symbol='HPG')

    def test_get_stocks(self):
        url = reverse('api_admin:stock-list')
        response = self.get(url)
        self.assertEqual(response.data['paging']['count'], 2)
        self.assertEqual(response.data['items'][0]['name'], 'HPG')
        self.assertEqual(response.data['items'][1]['name'], 'Ngan Hang VCB')

    def test_get_stock(self):
        url = reverse('api_admin:stock-detail', args=[self.stock1.pk])

        response = self.get(url)
        self.assertIsNotNone(response.data['name'])

    def test_create_stock(self):
        url = reverse('api_admin:stock-list')
        response = self.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': 'Ngan Hang ACB',
            'description': 'Description ACB',
            'symbol': 'ACB',
            'photo': self.generate_photo_file(),
            'exchange': 'hose'
        }

        response = self.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        count = Stock.objects.all().count()
        self.assertEqual(count, 3)

        stock = Stock.objects.filter(symbol='ACB').first()
        self.assertEqual(stock.name, 'Ngan Hang ACB')
        self.assertEqual(stock.symbol, 'ACB')

    def test_update_stock(self):
        data = {
            'name': 'Ngan Hang CP VCB',
        }
        url = reverse('api_admin:stock-detail', args=[self.stock1.pk])
        response = self.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Ngan Hang CP VCB')

    def test_delete_stock(self):
        url = reverse('api_admin:stock-detail', args=[self.stock1.pk])
        response = self.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        count = Stock.objects.all().count()
        self.assertEqual(count, 1)
