from django.test import TestCase

from core.services.industry.get_industries import GetIndustriesService
from tests.factories.industry import IndustryFactory
from tests.factories.industry_analytics import IndustryAnalyticsFactory


class GetIndustriesServiceTestCase(TestCase):
    def setUp(self):
        industry1 = IndustryFactory(name="Dầu khí", slug='dau-khi', level=1, icb_code='0001')
        industry2 = IndustryFactory(name="Nguyên vật liệu", slug='nguyen-vat-lieu', level=1, icb_code='1000')

        industry3 = IndustryFactory(name="Hóa chất", slug='hoa-chat', level=2, icb_code='1300', parent=industry1)
        industry4 = IndustryFactory(name="Tài nguyên Cơ bản", slug='tai-nguyen-co-ban', level=2, icb_code='1700', parent=industry1)

        IndustryAnalyticsFactory(industry_id=industry1.id, icb_code='0001', change_percentage_1w=5, pe=5)
        IndustryAnalyticsFactory(industry_id=industry2.id, icb_code='1000', change_percentage_1w=6, pe=5.6)
        IndustryAnalyticsFactory(industry_id=industry3.id, icb_code='1300', change_percentage_1w=7, pe=7)
        IndustryAnalyticsFactory(industry_id=industry4.id, icb_code='1700', change_percentage_1w=8, pe=8)

        super(GetIndustriesServiceTestCase, self).setUp()

    def test_get_industries(self):
        filters = [
            {'name': 'level', 'operator': 'eq', 'value': 2},
        ]
        sorts = [
            {'name': 'change_percentage_1w', 'type': 'desc'}
        ]
        fields = ['name', 'icb_code', 'change_percentage_1w', 'pe']
        result = GetIndustriesService(fields=fields, filters=filters, sorts=sorts).call()

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].icb_code, "1700")
        self.assertEqual(result[0].change_percentage_1w, 8)
        self.assertEqual(result[0].name, "Tài nguyên Cơ bản")

        self.assertEqual(result[1].icb_code, "1300")
        self.assertEqual(result[1].change_percentage_1w, 7)
        self.assertEqual(result[1].name, "Hóa chất")
