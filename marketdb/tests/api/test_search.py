from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from tests.testutils.apitest import APITest

from core.models.search_index import SearchIndex
from core.services.search.search_index import generate_search_vector
from tests.factories.stock import StockFactory


class SearchApiTestCase(APITest):
    def setUp(self):
        super(SearchApiTestCase, self).setUp()

        self.stock1 = StockFactory(symbol="ACB", name="Ngan hang co phan A Chau")
        self.stock2 = StockFactory(symbol="VCB", name="Ngan hang vietcombank")
        self.stock3 = StockFactory(symbol="PIS", name="Tổng Công ty Pisico Bình Định - CTCP")
        self.stock4 = StockFactory(symbol="HPG", name="Thep Hoa Phat")
        self.stock5 = StockFactory(symbol="SPH", name="CTCP Xuất nhập khẩu Thủy sản Hà Nội")

        self.item1 = SearchIndex.objects.create(
            symbol="ACB", name="Ngan hang co phan A Chau",
            search_vector=generate_search_vector("ACB", "Ngan hang co phan A Chau", "ACB")
        )
        self.item2 = SearchIndex.objects.create(
            symbol="VCB", name="Ngan hang vietcombank",
            search_vector=generate_search_vector("VCB", "Ngan hang vietcombank", "VCB")
        )
        self.item3 = SearchIndex.objects.create(
            symbol="PIS", name="Tổng Công ty Pisico Bình Định - CTCP",
            search_vector=generate_search_vector("PIS", "Tổng Công ty Pisico Bình Định - CTCP", "PIS")
        )
        self.item4 = SearchIndex.objects.create(
            symbol="HPG", name="Thep Hoa Phat",
            search_vector=generate_search_vector("HPG", "Thep Hoa Phat", "HPG")
        )
        self.item5 = SearchIndex.objects.create(
            symbol="SPH", name="CTCP Xuất nhập khẩu Thủy sản Hà Nội",
            search_vector=generate_search_vector("SPH", "CTCP Xuất nhập khẩu Thủy sản Hà Nội", "SPH")
        )

        self.client = APIClient()

    def test_get_search_results_success(self):
        url = reverse('api:search') + "?keyword=p"
        response = self.client.get(url)

        self.assertEqual(response.data['paging']['count'], 4)
        self.assertEqual(response.data['items'][0]['detail']['name'], self.item3.name)
        self.assertEqual(response.data['items'][0]['symbol'], self.item3.symbol)
        self.assertEqual(response.data['items'][1]['detail']['name'], self.item4.name)
        self.assertEqual(response.data['items'][1]['symbol'], self.item4.symbol)
        self.assertEqual(response.data['items'][2]['detail']['name'], self.item5.name)
        self.assertEqual(response.data['items'][2]['symbol'], self.item5.symbol)

        url = reverse('api:search') + "?keyword=ph"
        response = self.client.get(url)
        self.assertEqual(response.data['paging']['count'], 3)
        self.assertEqual(response.data['items'][0]['detail']['name'], self.item1.name)
        self.assertEqual(response.data['items'][0]['symbol'], self.item1.symbol)
        self.assertEqual(response.data['items'][1]['detail']['name'], self.item4.name)
        self.assertEqual(response.data['items'][1]['symbol'], self.item4.symbol)
        self.assertEqual(response.data['items'][2]['detail']['name'], self.item5.name)
        self.assertEqual(response.data['items'][2]['symbol'], self.item5.symbol)

        url = reverse('api:search') + "?keyword=CB"
        response = self.client.get(url)
        self.assertEqual(response.data['paging']['count'], 2)
        self.assertEqual(response.data['items'][0]['symbol'], self.item1.symbol)
        self.assertEqual(response.data['items'][1]['symbol'], self.item2.symbol)

    def test_get_search_results_failed(self):
        url = reverse('api:search') + "?keyword="
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

        url = reverse('api:search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
