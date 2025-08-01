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
        return cls(2023, 2, 14)


date = TodayMock


class FearGreedIndexTestCase(APITest):
    def setUp(self):
        super(FearGreedIndexTestCase, self).setUp()

        FearGreedIndexFactory(date=datetime(2023, 2, 16), score=97)
        FearGreedIndexFactory(date=datetime(2023, 2, 15), score=96)
        FearGreedIndexFactory(date=datetime(2023, 2, 14), score=95)
        FearGreedIndexFactory(date=datetime(2023, 2, 12), score=94)
        FearGreedIndexFactory(date=datetime(2023, 2, 7), score=83)
        FearGreedIndexFactory(date=datetime(2023, 1, 15), score=62)
        FearGreedIndexFactory(date=datetime(2023, 1, 14), score=61)
        FearGreedIndexFactory(date=datetime(2022, 2, 15), score=71)
        FearGreedIndexFactory(date=datetime(2022, 2, 14), score=70)

        self.client = APIClient()

    def test_get_fear_greed_index_daily(self):
        url = reverse('api:fear-greed-index')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 97)

    # @mock.patch('common.utils.datetime_util.get_datetime_now')
    # def test_get_fear_greed_index_historical_values(self, today_mock):
    #     today_mock.return_value = datetime(2023, 2, 15)
    #
    #     url = reverse('api:fear-greed-index-historical-values')
    #     response = self.client.get(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data[0]['fear_greed_index']['score'], 97)
    #     self.assertEqual(response.data[1]['fear_greed_index']['score'], 83)
    #     self.assertEqual(response.data[2]['fear_greed_index']['score'], 62)
    #     self.assertEqual(response.data[3]['fear_greed_index']['score'], 71)
