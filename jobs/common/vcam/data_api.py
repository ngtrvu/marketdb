import pandas as pd

from common.tinydwh.datetime_util import get_date_str, VN_TIMEZONE, get_previous_date_str
from common.vcam.client import VCAMClient
from common.vcam.config import VCAMConfig
from common.vcam import model


class VCAMDataApi:
    date_format = "%d/%m/%Y"

    def __init__(self, api_token, access_code, host):
        self.api_token = api_token
        self.access_code = access_code
        self.config = VCAMConfig(api_token=api_token, access_code=access_code, host=host)
        self.client = VCAMClient(self.config)

    def business_performance(self):
        params = model.business_performance

        res = self.client.business_performance(_input_data={}, _object=params)
        return res

    def fund_performance(self, fund_code: str, from_date: str, to_date: str, order_type: int = 1,
                         per_page: int = 10, page: int = 1):
        params = model.fund_performance
        params["fund_code"] = fund_code
        params["from_date"] = from_date
        params["to_date"] = to_date
        params["order_type"] = order_type
        params["per_page"] = per_page
        params["page"] = page

        res = self.client.fund_performance(_input_data={}, _object=params)
        return res

    def fund_performance_latest_month(self, fund_code: str, order_type: int = 1, per_page: int = 10, page: int = 1) -> pd.DataFrame:
        to_date: str = get_date_str(tz=VN_TIMEZONE, date_format=self.date_format)
        from_last_30_days: str = get_previous_date_str(
            input_date=to_date, tz=VN_TIMEZONE, date_format=self.date_format, n_day=30)

        params = model.fund_performance
        params["fund_code"] = fund_code
        params["from_date"] = from_last_30_days
        params["to_date"] = to_date
        params["order_type"] = order_type
        params["per_page"] = per_page
        params["page"] = page

        res = self.client.fund_performance(_input_data={}, _object=params)
        return res
