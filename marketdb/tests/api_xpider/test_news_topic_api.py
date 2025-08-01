from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.testutils.apitest import APITest
from tests.factories.news import (
    NewsPostFactory, NewsTopicFactory, NewsTrendingFactory
)


class NewsTopicApiTestCase(APITest):
    def setUp(self):
        super(NewsTopicApiTestCase, self).setUp()

        self.news1 = NewsPostFactory(title="ACB", doc_id=1, is_relevant=True, relevant_score=0.9)
        self.news2 = NewsPostFactory(title="Việt_Nam", doc_id=2, is_relevant=True, relevant_score=0.9)
        self.news3 = NewsPostFactory(title="Fed ACB HPG", doc_id=3, is_relevant=True, relevant_score=0.6)
        self.news4 = NewsPostFactory(title="ACBD", doc_id=4, is_relevant=False, relevant_score=0.4)

        self.news_topic = NewsTopicFactory(topic_token='ACB', doc_id=1)
        self.news_topic2 = NewsTopicFactory(topic_token='ACB', doc_id=3)
        # self.news_topic3 = NewsTopicFactory(topic_token='HPG', doc_id=3)

        self.news_trending = NewsTrendingFactory(doc_id=1)

        self.client = APIClient()

    def test_news_api(self):
        url = reverse('api_xpider:news-topic')
        url += '?topic=ACB'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data['items']), 2)
        #
        # url = reverse('api:news-topic')
        # url += '?topic=HPG,ACB'
        # response = self.client.get(url)
        #
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data['items']), 1)

    def test_news_filter_by_topic_api(self):
        url = reverse('api_xpider:news-filter')
        url += '?topic=ACB'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data['items']), 2)

        url = reverse('api_xpider:news-filter')
        url += '?topic=HPG'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)
        # self.assertEqual(len(response.data['items']), 1)
        #
        # url = reverse('api_xpider:news-filter')
        # url += '?topic=HPG,ACB'
        # response = self.client.get(url)
        #
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data['items']), 1)

    def test_news_trending_api(self):
        url = reverse('api_xpider:news-trending')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data['items']), 1)
