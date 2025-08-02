import json
import requests
from datetime import datetime
from fake_headers import Headers

from common.tinydwh.datetime_util import get_datetime_now, VN_TIMEZONE


class ExternalTradingDateUtils:
    """TradingDateUtils: some utils for better trading date checking
    """

    def check_trading_date(self, datetime_obj: datetime = None):
        """Check trading time by external sources. We use DC for now. Later, we can change it by others or combine
        multiple check in case we need to fallback to ask external system about the trading time. We check ourselves
        in the first place
        """

        if datetime_obj:
            raise Exception("No external sources for checking trading time by date")

        symbol = 'E1VFVN30'
        url = f"https://api.dragoncapital.com.vn/iindex/getLatestIIndex.php?index={symbol}"
        headers = self.__build_crawler_header()

        response = requests.request("GET", url, headers=headers)
        dict_data = json.loads(response.text)
        trading_date = dict_data.get(symbol, {}).get('trade_date')
        datetime_now = get_datetime_now(tz=VN_TIMEZONE)
        today_8am = datetime_now.replace(hour=8, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

        if trading_date >= today_8am:
            return True

        return False

    def __build_crawler_header(self) -> dict:
        headers = Headers(browser="chrome", os="win", headers=True)
        headers = headers.generate()
        headers['Content-Type'] = 'application/json'

        return headers
