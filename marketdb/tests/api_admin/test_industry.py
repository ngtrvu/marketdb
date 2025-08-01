from django.urls import reverse
from rest_framework import status

from core.models.industries.industry import Industry
from tests.testutils.apitest import AdminAPITest
from tests.factories.industry import IndustryFactory


class IndustryTestCase(AdminAPITest):
    def setUp(self):
        super(IndustryTestCase, self).setUp()

        self.industry1 = IndustryFactory(name="ABC1", slug='abc1', level=1)
        self.industry2 = IndustryFactory(name="XYZ2", slug='xyz2', level=2)
        self.industry3 = IndustryFactory(name="ABC3", slug='abc3', level=3)
        self.industry4 = IndustryFactory(name="ABC4", slug='abc4', level=4, parent=self.industry3)
        self.industry5 = IndustryFactory(name="ABC5", slug='abc5', level=4, parent=self.industry3)

    def test_get_industries(self):
        url = reverse('api_admin:industry-list')
        response = self.get(url)
        self.assertEqual(response.data['paging']['count'], 5)

    def test_get_industry(self):
        url = reverse('api_admin:industry-detail', args=[self.industry2.pk])

        response = self.get(url)
        self.assertIsNotNone(response.data['name'])

    def test_create_industry(self):
        url = reverse('api_admin:industry-list')
        response = self.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': 'test',
            'slug': 'test',
            'level': 1,
            'icb_code': 5033,
            'photo': self.generate_photo_file(),
        }

        response = self.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        count = Industry.objects.count()
        self.assertEqual(count, 6)

    def test_update_industry(self):
        data = {
            'name': 'test2',
        }
        url = reverse('api_admin:industry-detail', args=[self.industry1.pk])
        response = self.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['name'], 'test2')

    def test_delete_industry(self):
        url = reverse('api_admin:industry-detail', args=[self.industry1.pk])
        response = self.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        count = Industry.objects.all().count()
        self.assertEqual(count, 4)
