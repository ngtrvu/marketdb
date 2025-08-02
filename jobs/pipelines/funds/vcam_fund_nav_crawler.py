import json
import logging
import os

import pandas as pd
import pytz
from dateutil import parser
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str, \
    get_previous_date_str
from common.tinydwh.storage.connector import GCS
from common.vcam.data_api import VCAMDataApi
from config import Config


class VcamNAVCrawler(MiniJobBase):
    """
    This is crawler the daily NAV
    """
    data_directory: str = "marketdb/fund_nav_daily"

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0, api_token: str = '', access_code: str = '',
                 host: str = ''):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.api_token = os.environ.get('VCAM_API_TOKEN', '') if not api_token else api_token
        self.access_code = os.environ.get('VCAM_ACCESS_CODE', '') if not access_code else api_token
        self.host = os.environ.get('VCAM_HOST', '') if not host else host

        super().__init__()

    def pipeline(self, input_date: str = None,
                 from_date: str = None, to_date=None, fund_code: str = "vcambf"):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if fund_code and type(fund_code) == str:
            symbol = fund_code.upper()
        else:
            logging.warning("Error: no fund_code")
            return

        if not self.api_token or not self.access_code:
            logging.warning("Error: not found VCAM_API_TOKEN or VCAM_ACCESS_CODE")
            return

        if not from_date and not to_date:
            to_date = get_date_str(date_format="%d-%m-%Y", tz=VN_TIMEZONE)
            from_date = get_previous_date_str(
                input_date=to_date, date_format="%d-%m-%Y", tz=VN_TIMEZONE, n_day=90)

        data_api = VCAMDataApi(
            api_token=self.api_token,
            access_code=self.access_code,
            host=self.host
        )
        response = data_api.fund_performance(
            fund_code=fund_code,
            from_date=from_date,
            to_date=to_date
        )
        self.transform_response_to_df(response=response, fund_code=fund_code)

        if not self.data_frame.empty:
            items = self.data_frame.apply(self.transform_row, axis=1)
            data = items.to_json(orient="records", lines=True)
            self.do_upload_gcs(data=data, input_date=input_date, symbol=symbol)

            logging.info(f"VcamNAVCrawler is successfully executed")
            return True
        
        logging.warning("Error: no data is loaded")
        return False

    def transform_response_to_df(self, response, fund_code):
        data = response.get("data", [])
        if data and len(data) > 0:
            df = pd.DataFrame(data)
            # preprocess data
            df = df[df['fund_code'] == fund_code]
            df = df.sort_values(["posting_date_value"])

        else:
            df = pd.DataFrame()

        self.data_frame = df.copy()
        return df

    def transform_row(self, row: dict) -> dict:
        row = self.fill_row_na(row)

        symbol = row["fund_code"].upper()
        nav_per_share = row.get("nav_certificate")

        fund_datetime = row.get("posting_date")
        if not fund_datetime:
            raise Exception("datetime is missing")

        if type(fund_datetime) == str:
            fund_datetime = parser.parse(row.get("posting_date"), dayfirst=True)

        # make sure datetime is tz-aware datetime
        timezone = pytz.timezone(VN_TIMEZONE)
        fund_datetime = timezone.localize(fund_datetime)
        fund_date = fund_datetime.strftime("%Y-%m-%d")

        return {
            "symbol": symbol,
            "date": fund_date,
            "datetime": fund_date,
            "nav": nav_per_share,
        }

    def do_upload_gcs(self, data: str, input_date: str, symbol: str):
        gcs = GCS()
        gcs_path = f"{self.data_directory}/{input_date}/fund_{symbol}.json"

        bucket_name = Config.BUCKET_NAME
        if not bucket_name:
            logging.error("Bucket name is not configured")

        gcs.upload_dict(
            dict_json=data, bucket_name=bucket_name, gcs_path=gcs_path
            # type: ignore
        )
        logging.info(f"Uploaded BUCKET=[{bucket_name}], PATH={gcs_path} to GCS...")
        return True
