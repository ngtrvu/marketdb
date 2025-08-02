import logging
import math
from datetime import datetime

import pandas as pd
from dateutil import parser
from pandas import DataFrame
from pytz import timezone

from common.tinydwh.base import MiniJobBase
from common.tinydwh.data import sub_dict
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    ensure_tzaware_datetime,
    get_date_str,
    str_to_datetime,
)
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class StockPriceIntradayJob(MiniJobBase):
    """Exchange price data updated from exchange. First, we leverage SSI iBoard. We may change it later"""

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(f"StockPriceIntradayJob: No trading today {input_date}...")
            return True

        self.new_lines = True
        self.load(
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_price_intraday",
            file_name_prefix="stock_price_ohlc.json",
        )

        # Stock Price Realtime
        stock_price_df = self.data_frame
        if stock_price_df.empty:
            logging.warning("StockPriceIntradayJob Error: no data is loaded")
            return False

        items = stock_price_df.apply(self.transform_row, axis=1)
        # Index Realtime Stock Price to db, closing values to realtime price make sure we provide the
        self.do_indexing(items)
        logging.info(
            f"StockPriceIntradayJob: Stock Price Realtime is successfully executed"
        )
        return True

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

    def get_closed_date(self, trading_date=None, date_format="%Y/%m/%d"):
        datetime_obj = datetime.now(tz=timezone(VN_TIMEZONE))
        if trading_date:
            datetime_obj = str_to_datetime(trading_date, date_format, tz=VN_TIMEZONE)
        return datetime_obj.replace(hour=15, minute=0, second=0)

    def fill_row_na(self, row: dict):
        filled_row = {}
        for key, val in row.items():
            if type(val) == float and math.isnan(val):
                filled_row[key] = 0
            else:
                filled_row[key] = val
        return filled_row

    def _get_type(self, stock_type: str):
        if not stock_type:
            return None

        if stock_type.lower() == "stock":
            return "stock"
        elif stock_type.lower() == "etf":
            return "etf"
        elif stock_type.lower() == "index":
            return "index"
        return None

    def transform_row(self, row: dict) -> dict:
        row = self.fill_row_na(row)

        stock_datetime = row.get("timestamp")
        if not stock_datetime:
            raise Exception("timestamp is missing")

        # make sure timestamp is tz-aware timestamp
        stock_datetime = ensure_tzaware_datetime(stock_datetime, tz=VN_TIMEZONE)

        # double-check the trading date value. In case, the timestamp is late against the closed trading time, we fix it.
        trading_date_str = get_date_str(stock_datetime, date_format="%Y-%m-%d")
        closed_datetime = self.get_closed_date(
            trading_date=trading_date_str, date_format="%Y-%m-%d"
        )
        if stock_datetime > closed_datetime:
            stock_datetime = closed_datetime

        price = row.get("close") if row.get("close") else row.get("reference")
        reference = row.get("reference")
        change_percentage_1d = None
        if price and reference and price > 0 and reference > 0:
            change_percentage_1d = round((price - reference) * 100 / reference, 2)

        return {
            "symbol": row["symbol"],
            "exchange": row["exchange"],
            "date": trading_date_str,
            "datetime": stock_datetime,
            "price": price,
            "type": self._get_type(row.get("type")),
            "reference": row.get("reference"),
            "change_percentage_1d": change_percentage_1d,
            "floor": row.get("floor"),
            "ceiling": row.get("ceiling"),
            "open": row.get("open") if row.get("open") else None,
            "high": row.get("high") if row.get("high") else None,
            "low": row.get("low") if row.get("low") else None,
            "close": row.get("close") if row.get("close") else None,
            "fb_volume": row.get("fb_volume", 0),
            "fs_volume": row.get("fs_volume", 0),
            "foreign_room": row.get("foreign_room", 0),
            "volume": row.get("volume", 0),
            "total_trading_value": row.get("volume", 0) * row.get("close", 0),
        }

    def do_indexing(self, items: pd.Series):
        symbols = {}
        symbol_values = self.marketdb_client.get_stock_items(
            key_fields=["symbol", "exchange"]
        )
        for stock in symbol_values:
            symbols[stock["symbol"]] = stock["exchange"]

        symbol_values = self.marketdb_client.get_etf_items(
            key_fields=["symbol", "exchange"]
        )
        for etf in symbol_values:
            symbols[etf["symbol"]] = etf["exchange"]

        selected_fields = [
            "symbol",
            "datetime",
            "price",
            "exchange",
            "type",
            "open",
            "high",
            "low",
            "close",
            "reference",
            "ceiling",
            "floor",
            "volume",
            "fb_volume",
            "fs_volume",
            "foreign_room",
            "total_trading_value",
            "change_percentage_1d",
        ]

        payload_items = []
        for item in items:
            symbol = item.get("symbol")
            if not symbol:
                continue
            payload_items.append(sub_dict(selected_fields, item))

        if len(payload_items) > 0:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="StockPriceRealtime",
                key_fields=["symbol"],
                payload=payload_items,
            )
            if not success:
                logger.error(f"StockPriceRealtime update error: {response}")
