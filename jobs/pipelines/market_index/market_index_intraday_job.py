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


class MarketIndexIntradayJob(MiniJobBase):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    input_date: str

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        
        if not self.is_trading_date(date_str=input_date):
            logger.info(f"MarketIndexIntradayJob: No trading today {input_date}...")
            return True
        
        self.input_date = input_date
        self.new_lines = True

        # TODO: load data from iboard instead of vndirect which does't have enough index data
        self.load(
            input_date=self.input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/market_index_ohlc",
        )

        # Market Index Intraday
        if self.data_frame.empty:
            logger.warning("MarketIndexIntradayJob Error: no data is loaded")
            return False

        items = self.data_frame.apply(self.vndirect_transform_row, axis=1).tolist()

        indexing_success = self.do_indexing(items)
        if not indexing_success:
            logger.error(f"MarketIndexIntradayJob Error Indexing.")
            return False

        logger.info(f"MarketIndexIntradayJob is successfully executed.")
        return True

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

    def get_closed_date(self, trading_date: str=None, date_format="%Y/%m/%d"):
        datetime_obj = datetime.now(tz=timezone(VN_TIMEZONE))
        if trading_date:
            datetime_obj = str_to_datetime(trading_date, date_format, tz=VN_TIMEZONE)
        return datetime_obj.replace(hour=15, minute=0, second=0)

    def vndirect_transform_row(self, row: dict) -> dict:
        row = self.fill_row_na(row)

        stock_datetime = self.input_date
        if isinstance(stock_datetime, str):
            stock_datetime = isostring_to_datetime(stock_datetime)

        # make sure datetime is tz-aware datetime
        stock_datetime = ensure_tzaware_datetime(stock_datetime, tz=VN_TIMEZONE)

        # double-check the trading date value. In case, the datetime is late against the closed trading time, we fix it.
        trading_date_str = get_date_str(stock_datetime, date_format="%Y-%m-%d")
        closed_datetime = self.get_closed_date(
            trading_date=trading_date_str, date_format="%Y-%m-%d"
        )
        if stock_datetime > closed_datetime:
            stock_datetime = closed_datetime

        change_percentage_1d = None
        if row.get("open"):
            change_percentage_1d = (
                (row.get("value") - row.get("open")) * 100.0 / row.get("open")
            )
            change_percentage_1d = round(change_percentage_1d, 4)

        return {
            "symbol": row["symbol"],
            "exchange": row["exchange"],
            "date": stock_datetime.date(),
            "datetime": stock_datetime,
            "price": row.get("value"),
            "type": "index",
            "reference": row.get("open"),
            "open": row.get("open"),
            "high": None,
            "low": None,
            "close": row.get("close"),
            "change_percentage_1d": change_percentage_1d,
            "volume": row.get("totalVolume", 0),
            "total_trading_value": row.get("totalValue", 0),
        }

    def transform_fiin_row(self, row: dict) -> dict:
        row = self.fill_row_na(row)

        stock_datetime = row.get("timestamp")
        if not stock_datetime:
            raise Exception("timestamp is missing")

        if type(stock_datetime) == str:
            stock_datetime = isostring_to_datetime(stock_datetime)

        # make sure datetime is tz-aware datetime
        stock_datetime = ensure_tzaware_datetime(stock_datetime, tz=VN_TIMEZONE)

        # double-check the trading date value. In case, the datetime is late against the closed trading time, we fix it.
        trading_date_str = get_date_str(stock_datetime, date_format="%Y-%m-%d")
        closed_datetime = self.get_closed_date(
            trading_date=trading_date_str, date_format="%Y-%m-%d"
        )
        if stock_datetime > closed_datetime:
            stock_datetime = closed_datetime

        price = row.get("close") if row.get("close") else row.get("reference")
        reference = row.get("referenceIndex")
        change_percentage_1d = None
        if price and reference and price > 0 and reference > 0:
            change_percentage_1d = round((price - reference) * 100 / reference, 2)

        return {
            "symbol": row["comGroupCode"],
            "date": stock_datetime.date(),
            "datetime": stock_datetime,
            "price": row.get("indexValue"),
            "type": "index",
            "reference": row.get("referenceIndex"),
            "open": row.get("openIndex") if row.get("openIndex") else None,
            "high": row.get("highestIndex") if row.get("highestIndex") else None,
            "low": row.get("lowestIndex") if row.get("lowestIndex") else None,
            "close": row.get("closeIndex") if row.get("closeIndex") else None,
            "change_percentage_1d": change_percentage_1d,
            "volume": row.get("totalMatchVolume", 0),
            "total_trading_value": row.get("totalMatchValue", 0),
        }

    def do_indexing(self, items: list):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="StockPriceRealtime",
                key_fields=["symbol"],
                payload=items,
            )

            if not success:
                logger.error(f"Error indexing: {response}")
                return False

            logger.debug(f"Indexing response: {response}")
            return True

        except Exception as ex:
            logger.error(f"Error indexing: {ex}")
            return False
