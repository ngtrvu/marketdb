from django.urls import reverse
from rest_framework.test import APIClient
from tests.testutils.apitest import APITest

from tests.factories.industry import IndustryFactory
from tests.factories.industry_analytics import IndustryAnalyticsFactory


class ScreenerIndustriesApiTestCase(APITest):

    def setUp(self):
        super(ScreenerIndustriesApiTestCase, self).setUp()

        industry1 = IndustryFactory(id=10001, name="Dầu khí", slug='dau-khi', level=1, icb_code='0001')
        industry2 = IndustryFactory(id=11000, name="Nguyên vật liệu", slug='nguyen-vat-lieu', level=1, icb_code='1000')

        industry3 = IndustryFactory(id=11300, name="Hóa chất", slug='hoa-chat', level=2, icb_code='1300', parent=industry1)
        industry4 = IndustryFactory(id=11700, name="Tài nguyên Cơ bản", slug='tai-nguyen-co-ban', level=2, icb_code='1700', parent=industry1)

        IndustryAnalyticsFactory(industry_id=industry1.id, icb_code='0001', change_percentage_1w=5, pe=5)
        IndustryAnalyticsFactory(industry_id=industry2.id, icb_code='1000', change_percentage_1w=6, pe=5.6)
        IndustryAnalyticsFactory(industry_id=industry3.id, icb_code='1300', change_percentage_1w=7, pe=7)
        IndustryAnalyticsFactory(industry_id=industry4.id, icb_code='1700', change_percentage_1w=8, pe=8)

        self.client = APIClient()

    def test_get_screener_market_indexes(self):
        base_url = reverse('api:screener-industries')
        filter_config = "fields=id,name,icb_code,change_percentage_1w,pe&filters=level__eq__2&sorts=change_percentage_1w__desc"
        url = f"{base_url}?{filter_config}"
        response = self.client.get(url)

        self.assertEqual(response.data['items'][0]['id'], 11700)
        self.assertEqual(response.data['items'][0]['icb_code'], "1700")
        self.assertEqual(float(response.data['items'][0]['change_percentage_1w']), 8)
        self.assertEqual(response.data['items'][0]['name'], "Tài nguyên Cơ bản")

        self.assertEqual(response.data['items'][1]['id'], 11300)
        self.assertEqual(response.data['items'][1]['icb_code'], "1300")
        self.assertEqual(float(response.data['items'][1]['change_percentage_1w']), 7)
        self.assertEqual(response.data['items'][1]['name'], "Hóa chất")
