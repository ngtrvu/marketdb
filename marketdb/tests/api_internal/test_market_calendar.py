import unittest

from pytz import timezone
from datetime import datetime
from django.urls import reverse
from rest_framework import status

from common.utils.datetime_util import VN_TIMEZONE
from tests.testutils.apitest import AdminAPITest
from core.models.market.market_calendar import MarketStatusEnum
from tests.factories.market_calendar import MarketCalendarFactory


class MarketCalendarTestCase(AdminAPITest):
    def setUp(self):
        super(MarketCalendarTestCase, self).setUp()

        tz_info = timezone(VN_TIMEZONE)

        MarketCalendarFactory(date=datetime(2023, 4, 24, tzinfo=tz_info).date(), status=MarketStatusEnum.OPEN)
        MarketCalendarFactory(date=datetime(2023, 4, 25, tzinfo=tz_info).date(), status=MarketStatusEnum.OPEN)
        MarketCalendarFactory(date=datetime(2023, 4, 26, tzinfo=tz_info).date(), status=MarketStatusEnum.OPEN)
        MarketCalendarFactory(date=datetime(2023, 4, 27, tzinfo=tz_info).date(), status=MarketStatusEnum.OPEN)
        MarketCalendarFactory(date=datetime(2023, 4, 28, tzinfo=tz_info).date(), status=MarketStatusEnum.OPEN)
        MarketCalendarFactory(date=datetime(2023, 4, 29, tzinfo=tz_info).date(), status=MarketStatusEnum.CLOSE)
        MarketCalendarFactory(date=datetime(2023, 4, 30, tzinfo=tz_info).date(), status=MarketStatusEnum.CLOSE)
        MarketCalendarFactory(date=datetime(2023, 5, 1, tzinfo=tz_info).date(), status=MarketStatusEnum.CLOSE)
        MarketCalendarFactory(date=datetime(2023, 5, 2, tzinfo=tz_info).date(), status=MarketStatusEnum.CLOSE)
        MarketCalendarFactory(date=datetime(2023, 5, 3, tzinfo=tz_info).date(), status=MarketStatusEnum.CLOSE)

    def test_check_market_calendar(self):
        url = reverse('api_internal:market-calendar-detail', args=["2023-04-22"])
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MarketStatusEnum.CLOSE)  # saturday

        url = reverse('api_internal:market-calendar-detail', args=["2023-04-23"])
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MarketStatusEnum.CLOSE)  # sunday

        url = reverse('api_internal:market-calendar-detail', args=["2023-04-24"])
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MarketStatusEnum.OPEN)  # in our calendar db

        url = reverse('api_internal:market-calendar-detail', args=["2023-05-01"])
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MarketStatusEnum.CLOSE)  # in our calendar db

        url = reverse('api_internal:market-calendar-detail', args=["2023-05-03"])
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MarketStatusEnum.CLOSE)  # in our calendar db

        url = reverse('api_internal:market-calendar-detail', args=["2023-06-01"])
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], MarketStatusEnum.OPEN)  # not in our db, but not the weekend

        url = reverse('api_internal:market-calendar-detail', args=["2023-06"])
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = "/marketdb-internal/v1/market-calendar/xyz"
        response = self.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
