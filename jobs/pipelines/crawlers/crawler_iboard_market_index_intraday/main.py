import requests
import os

from common.tinydwh.storage.connector import GCS
from common.tinydwh.base import MiniJobBase
from utils.logger import setup_logger, logger
from common.tinydwh.datetime_util import (
    get_datetime_from_timestamp,
    get_datetime_now,
    get_date_str,
    VN_TIMEZONE,
)

setup_logger(level="INFO")

URL = "https://iboard-query.ssi.com.vn/exchange-index"


class IBoardMarketIndexIntraday(MiniJobBase):
    def __init__(self):
        self.bucket_name = os.environ.get("BUCKET_NAME", "stock_analytics")
        self.namespace = "crawler"

    def pipeline(self, input_date: str = ""):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=5)
        if response.status_code != 200:
            logger.error(response.text)
            return f"Failed to fetch data from {URL}", 500

        data = response.json()
        logger.info("Data fetched successfully")

        items = data.get("data", [])
        item = items[0] if items else {}
        if not item["time"]:
            logger.error(f"Failed to parse data from iBoard")
            return False

        timestamp = int(item["time"]) / 1000
        date_obj = get_datetime_from_timestamp(timestamp, tz=VN_TIMEZONE)
        date_dir = get_date_str(date_obj, date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        base_path = "crawler/iboard_market_index_intraday"
        filename = "iboard_market_index_intraday.json"

        gcs_path = f"{base_path}/{date_dir}/{filename}"
        GCS().upload_to_gcs(dict_data=items, bucket_name=self.bucket_name, gcs_path=gcs_path)

        logger.info(f"Data crawled and saved successfully: gs://{self.bucket_name}/{gcs_path}")
        return True
