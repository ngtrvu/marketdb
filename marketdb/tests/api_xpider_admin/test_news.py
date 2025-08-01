from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.testutils.apitest import AdminAPITest
from tests.factories.news import NewsPostFactory


class NewsApiTestCase(AdminAPITest):
    def setUp(self):
        super(NewsApiTestCase, self).setUp()

        self.news1 = NewsPostFactory(title="ACB", doc_id=1, is_relevant=True, is_recommend=True)
        self.news2 = NewsPostFactory(
            title="Việt_Nam", doc_id=2, is_relevant=True, is_recommend=True
        )
        self.news3 = NewsPostFactory(title="ACB", doc_id=3, is_relevant=False, is_recommend=False)

        self.client = APIClient()

    def test_get_news(self):
        # Add
        url = reverse("api_xpider_admin:posts-list")
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["items"][2]["doc_id"], "1")
        self.assertTrue(response.data["items"][2]["is_relevant"])
        self.assertTrue(response.data["items"][2]["is_recommend"])

        self.assertEqual(response.data["items"][1]["doc_id"], "2")
        self.assertTrue(response.data["items"][1]["is_relevant"])
        self.assertTrue(response.data["items"][1]["is_recommend"])

        self.assertEqual(response.data["items"][0]["doc_id"], "3")
        self.assertFalse(response.data["items"][0]["is_relevant"])
        self.assertFalse(response.data["items"][0]["is_recommend"])
