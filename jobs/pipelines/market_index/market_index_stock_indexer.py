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


class MarketIndexStockIndexer(MiniJobBase):

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()
        self.input_date: str = None

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.input_date = input_date

        # load all market index symbols
        self.new_lines = False
        symbols_df = self.load(
            input_date=self.input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="crawler/iboard_market_index",
        )

        if symbols_df.empty:
            logger.warning("MarketIndexStockIndexer Error: no symbol data is loaded")
            return False

        symbols = symbols_df[0].tolist()
        for symbol in symbols:
            stock_df = self.load(
                input_date=self.input_date,
                bucket_name=Config.BUCKET_NAME,
                base_path="crawler/iboard_market_index_group",
                file_name_prefix=f"{symbol}.json",
            )

            # only get stocks that are not ETFs or warrants
            stock_df = stock_df[stock_df['st'] == "s"]
            stocks = stock_df["ss"].tolist()

            indexing_success = self.do_indexing(symbol, stocks)
            if not indexing_success:
                logger.error(f"failed to index {symbol}")

        # Market index stock indexing
        if self.data_frame.empty:
            logger.warning("no data is loaded")
            return False

        logger.info("MarketIndexStockIndexer is successfully executed.")
        return True

    def do_indexing(self, index_symbol: str, symbols: list[dict]) -> bool:
        logger.info(f"Indexing {len(symbols)} stocks for {index_symbol}")
        payload = []
        for symbol in symbols:
            payload.append(
                {
                    "stock_id": symbol.upper(),
                    "market_index_id": index_symbol.upper(),
                    "modified": "2024-12-17 08:14:55.291855+00",
                }
            )
        self.marketdb_client.index_to_db_bulk(
            model_name="MarketIndexStock",
            key_fields=["stock_id", "market_index_id"],
            payload=payload,
        )
        return True
