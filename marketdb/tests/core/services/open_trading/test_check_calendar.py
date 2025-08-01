from pytz import timezone
from datetime import datetime
from django.urls import reverse
from rest_framework import status

from common.utils.datetime_util import VN_TIMEZONE
from tests.testutils.apitest import AdminAPITest
from core.services.open_trading.check_calendar import CheckCalendarService
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
        result = CheckCalendarService(date="2023-04-22").call()
        self.assertFalse(result)  # saturday

        result = CheckCalendarService(date="2023-04-23").call()
        self.assertFalse(result)  # sunday

        result = CheckCalendarService(date="2023-04-24").call()
        self.assertTrue(result)  # in our calendar db

        result = CheckCalendarService(date="2023-04-28").call()
        self.assertTrue(result)  # in our calendar db

        result = CheckCalendarService(date="2023-05-01").call()
        self.assertFalse(result)  # in our calendar db

        result = CheckCalendarService(date="2023-05-03").call()
        self.assertFalse(result)  # in our calendar db

        result = CheckCalendarService(date="2023-06-01").call()
        self.assertTrue(result)   # not in our db, but not the weekend

        result = CheckCalendarService(date="2023-06-01").call()
        self.assertTrue(result)  # not in our db, but not the weekend

        with self.assertRaises(Exception):
            CheckCalendarService(date="2023-06").call()
