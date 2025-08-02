import requests
import os
import random
import time

from common.tinydwh.storage.connector import GCS
from common.tinydwh.base import MiniJobBase
from utils.logger import setup_logger, logger
from common.tinydwh.datetime_util import (
    get_datetime_from_timestamp,
    get_datetime_now,
    get_date_str,
    VN_TIMEZONE,
)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}
MARKET_INDEX_URL = "https://iboard-query.ssi.com.vn/exchange-index"
MARKET_INDEX_GROUP_URL = "https://iboard-query.ssi.com.vn/v2/stock/group/"

setup_logger(level="INFO")


class IBoardMarketIndexGroup(MiniJobBase):
    def __init__(self):
        self.bucket_name = os.environ.get("BUCKET_NAME", "stock_analytics")
        self.namespace = "crawler"
        self.terminated = False
        self.input_date = ""

    def pipeline(self, input_date: str = ""):
        response = requests.get(MARKET_INDEX_URL, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            logger.error(response.text)
            return f"Failed to fetch data from {MARKET_INDEX_URL}", 500

        data = response.json()
        items = data.get("data", [])
        indexes = [item["indexId"] for item in items]
        logger.info(f"{len(indexes)} Market index symbols fetched successfully")

        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.input_date = input_date
        self.export_index_symbols_to_gcs(indexes)
        for index_symbol in indexes:
            if self.terminated:
                logger.info("Crawler is terminated")
                break

            # Random sleep time to avoid overloading the server
            random_seconds = random.randint(3, 15)
            logger.info(
                f"Sleeping for {random_seconds} seconds, before crawling data for index: {index_symbol}"
            )
            time.sleep(random_seconds)

            stocks = self.crawl_group_by_index(index_symbol)
            self.export_to_gcs(stocks, index_symbol)

    def crawl_group_by_index(self, index_symbol: str):
        url = f"{MARKET_INDEX_GROUP_URL}{index_symbol}"
        response = requests.get(url, headers=HEADERS, timeout=5)

        # termninate the service if status is 5xx
        if response.status_code >= 500:
            logger.error(f"Failed to fetch data from {url}: {response.text}")
            self.terminated = True
            return False

        if response.status_code != 200:
            logger.error(f"Failed to fetch data from {url}: {response.text}")
            return False

        data = response.json()
        items = data.get("data", [])
        return items

    def export_to_gcs(self, items: list[dict], index_symbol: str) -> bool:
        base_path = "crawler/iboard_market_index_group"
        filename = f"{index_symbol}.json"

        gcs_path = f"{base_path}/{self.input_date}/{filename}"
        GCS().upload_to_gcs(
            dict_data=items, bucket_name=self.bucket_name, gcs_path=gcs_path
        )

        logger.info(
            f"Data crawled and saved successfully: gs://{self.bucket_name}/{gcs_path}"
        )
        return True

    def export_index_symbols_to_gcs(self, items: list[dict]) -> bool:
        base_path = "crawler/iboard_market_index"
        filename = "market_index_symbols.json"

        gcs_path = f"{base_path}/{self.input_date}/{filename}"
        GCS().upload_to_gcs(
            dict_data=items, bucket_name=self.bucket_name, gcs_path=gcs_path
        )

        logger.info(
            f"Market index symbols saved successfully: gs://{self.bucket_name}/{gcs_path}"
        )
        return True
