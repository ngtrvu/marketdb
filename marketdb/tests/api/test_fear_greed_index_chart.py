from unittest import mock
from datetime import datetime, date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.testutils.apitest import APITest
from tests.factories.fear_greed_index import FearGreedIndexFactory


class TodayMock(date):
    @classmethod
    def today(cls):
        return cls(2023, 3, 9)


date = TodayMock


class FearGreedIndexChartTestCase(APITest):
    def setUp(self):
        super(FearGreedIndexChartTestCase, self).setUp()

        FearGreedIndexFactory(date=datetime(2022, 2, 14), score=70)
        FearGreedIndexFactory(date=datetime(2022, 2, 15), score=71)
        FearGreedIndexFactory(date=datetime(2023, 1, 14), score=61)
        FearGreedIndexFactory(date=datetime(2023, 1, 15), score=62)
        FearGreedIndexFactory(date=datetime(2023, 2, 7), score=83)
        FearGreedIndexFactory(date=datetime(2023, 2, 12), score=94)
        FearGreedIndexFactory(date=datetime(2023, 2, 14), score=95)
        FearGreedIndexFactory(date=datetime(2023, 2, 15), score=96)
        FearGreedIndexFactory(date=datetime(2023, 2, 16), score=97)
        FearGreedIndexFactory(date=datetime(2023, 3, 9), score=99)

        self.client = APIClient()

    def test_get_fear_greed_index_chart(self):
        url = reverse('api:fear-greed-index-daily')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 10)
        # head series
        self.assertEqual(response.data[0]['date'], '2022-02-14')
        self.assertEqual(response.data[0]['score'], 70)

        # tail series
        self.assertEqual(response.data[-1]['date'], '2023-03-09')
        self.assertEqual(response.data[-1]['score'], 99)
