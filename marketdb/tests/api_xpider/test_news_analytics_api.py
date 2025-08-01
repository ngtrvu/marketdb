from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.testutils.apitest import APITest


class AnalyticsApiTestCase(APITest):
    def setUp(self):
        super(AnalyticsApiTestCase, self).setUp()

        self.client = APIClient()

    def test_analytics_api_success(self):
        # self.assertEqual(1, 1)
        url = reverse('api_xpider:analytics-news')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data, {})

        self.assertTrue('sentiment_ratio' in response.data)
        self.assertTrue('negative_percentage' in response.data['sentiment_ratio'])
        self.assertTrue('positive_percentage' in response.data['sentiment_ratio'])
