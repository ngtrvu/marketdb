from django.urls import reverse
from rest_framework import status

from tests.testutils.apitest import AdminAPITest
from core.models.screener.collection import Collection
from tests.factories.collection import CollectionFactory


class CollectionTestCase(AdminAPITest):
    def setUp(self):
        super(CollectionTestCase, self).setUp()

        self.collection1 = CollectionFactory()
        self.collection2 = CollectionFactory()

    def test_get_products(self):
        url = reverse('api_admin:collection-list')
        response = self.get(url)
        self.assertEqual(response.data['paging']['count'], 2)

    def test_get_collection(self):
        url = reverse('api_admin:collection-detail', args=[self.collection2.pk])

        response = self.get(url)
        self.assertIsNotNone(response.data['title'])

    def test_create_collection(self):
        url = reverse('api_admin:collection-list')
        response = self.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'title': 'test',
            'slug': 'test',
            'order': 10,
            'photo': self.generate_photo_file(),
        }
        response = self.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        count = Collection.objects.all().count()
        self.assertEqual(count, 3)

    def test_update_collection(self):
        data = {
            'title': 'test2',
            'order': 7,
        }
        url = reverse('api_admin:collection-detail', args=[self.collection1.pk])
        response = self.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['title'], 'test2')
        self.assertEqual(response.data['order'], 7)

    def test_delete_collection(self):
        url = reverse('api_admin:collection-detail', args=[self.collection1.pk])
        response = self.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        count = Collection.objects.all().count()
        self.assertEqual(count, 1)
