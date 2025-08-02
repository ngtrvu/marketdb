import pandas as pd

from datetime import datetime
from pandas import DataFrame
from pytz import timezone

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    ensure_tzaware_datetime,
    get_date_str,
    str_to_datetime,
)
from utils.logger import logger
from common.mdb.client import MarketdbClient
from config import Config


class TradingInitializationJob(MiniJobBase):
    """
    This is for setting up the new trading day.
        + StockPriceRealtime need to be reset following the reference, the datetime value should be the opening time.
        This is used for stocks, ETFs, Market Indexes
        + Anything else: TBD
    """

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    symbols: dict = {}

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()

        super().__init__()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        is_trading_date = self.marketdb_client.check_calendar(datetime_obj)
        if not is_trading_date:
            logger.info(f"TradingInitializationJob: No trading today: {input_date}")
            return True

        # initialize intraday day, clear all previous trading date
        try:
            self.marketdb_client.initialize_intraday()
        except Exception as ex:
            logger.error(f"IntradayManager.initialize() error: {ex}")

        df = self.load_price_data(input_date)
        if df.empty:
            logger.warning("TradingInitializationJob: load_price_data no data")
            return False

        outstanding_shares_df = self.query_stocks_outstanding_shares()

        df.set_index(["symbol"], inplace=True)
        outstanding_shares_df.set_index(["symbol"], inplace=True)

        df.update(outstanding_shares_df)
        df.reset_index(inplace=True)  # to recover the initial structure

        if not df.empty:
            success = self.do_indexing(df)
            if not success:
                logger.info(f"TradingInitializationJob: indexing failed...")
                return False

            logger.info(
                f"TradingInitializationJob: Price data is successfully executed"
            )
            return True

        logger.warning("Error: no price data is loaded")
        return False

    def query_stocks_outstanding_shares(self) -> pd.DataFrame:

        stock_values = self.marketdb_client.get_stock_items(
            ["symbol", "exchange", "outstanding_shares"]
        )

        etf_values = self.marketdb_client.get_etf_items(
            ["symbol", "exchange", "outstanding_shares"]
        )

        market_index_values = self.marketdb_client.get_market_index_items()

        items = stock_values + etf_values + market_index_values

        df = pd.DataFrame.from_dict(items)
        df = df.sort_values(
            by=["symbol", "outstanding_shares"], ascending=[True, False]
        )
        df.drop_duplicates(subset=["symbol"], keep="first", inplace=True)

        return df

    def load_price_data(self, input_date) -> DataFrame:
        self.new_lines = True
        self.load(
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_price_intraday",
            file_name_prefix="stock_price_ohlc.json",
        )

        if self.data_frame.empty:
            logger.warning("TradingInitializationJob: load_price_data no data")
            return pd.DataFrame()

        data = self.data_frame.apply(self.transform_row, axis=1)
        return pd.DataFrame(data.to_list())

    def _get_opened_date(self, trading_date=None, date_format="%Y/%m/%d"):
        datetime_obj = datetime.now(tz=timezone(VN_TIMEZONE))
        if trading_date:
            datetime_obj = str_to_datetime(trading_date, date_format, tz=VN_TIMEZONE)
        return datetime_obj.replace(hour=9, minute=0, second=0)

    def _get_type(self, stock_type: str):
        if not stock_type:
            return None

        if stock_type.lower() == "stock":
            return "STOCK"
        elif stock_type.lower() == "etf":
            return "ETF"
        elif stock_type.lower() == "index":
            return "INDEX"
        return None

    def transform_row(self, row: dict) -> dict:
        row = self.fill_row_na(row)
        symbol = row["symbol"]

        # make sure datetime is tz-aware datetime
        stock_datetime = ensure_tzaware_datetime(row["timestamp"], tz=VN_TIMEZONE)

        # set the opened trading date
        stock_datetime = stock_datetime.replace(hour=9, minute=0, second=0)
        outstanding_shares = (
            self.symbols[symbol].get("outstanding_shares", 0)
            if symbol in self.symbols
            else 0
        )

        return {
            "symbol": row["symbol"],
            "date": stock_datetime.date(),
            "datetime": stock_datetime,
            "exchange": row["exchange"],
            "type": self._get_type(row.get("type")),
            "price": row.get("reference"),
            "reference": row.get("reference"),
            "ceiling": row.get("ceiling"),
            "floor": row.get("floor"),
            "volume": 0,
            "fb_volume": 0,
            "fs_volume": 0,
            "foreign_room": 0,  # not open time for trading then volume = 0
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "outstanding_shares": outstanding_shares,
        }

    def do_indexing(self, df: pd.DataFrame) -> bool:
        items = df.to_dict("records")
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
