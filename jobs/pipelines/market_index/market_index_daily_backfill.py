import math
import pandas as pd

from datetime import datetime
from pandas import DataFrame
from pytz import timezone

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    ensure_tzaware_datetime,
    get_date_str,
    isostring_to_datetime,
    str_to_datetime,
)
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class MarketIndexDailyBackfill(MiniJobBase):

    def __init__(self):
        self.marketdb_client = MarketdbClient()
        self.input_date: str = None

        super().__init__()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.input_date = input_date

        # load all market index symbols
        self.load(
            input_date=self.input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/market_index_ohlc_bulk",
        )

        if self.data_frame.empty:
            logger.warning("MarketIndexDailyBackfill Error: no symbol data is loaded")
            return False

        items = self.data_frame.apply(self.transform_row, axis=1).tolist()
        self.do_indexing(items)

        logger.info("MarketIndexDailyBackfill is successfully executed.")
        return True

    def transform_row(self, row: dict) -> dict:
        return {
            "symbol": row["symbol"],
            "date": row["date"], 
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],
            "value": row["volume"] * row["close"],
        }

    def do_indexing(self, items: list[dict]) -> bool:
        logger.info(f"Indexing {len(items)} items")
        payload = []
        for item in items:
            payload.append(
                {
                    "symbol": item["symbol"],
                    "datetime": item["date"],
                    "date": item["date"].strftime("%Y-%m-%d"),
                    "open": item["open"],
                    "high": item["high"],
                    "low": item["low"],
                    "close": item["close"],
                    "total_volume": item["volume"],
                    "total_value": item["value"],
                }
            )
        self.marketdb_client.index_to_db_bulk(
            model_name="MarketIndexDaily",
            key_fields=["symbol", "date"],
            payload=payload,
        )
        return True
