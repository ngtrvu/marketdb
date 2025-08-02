import pandas as pd
from pandas import DataFrame

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


class StockNewInitializer(MiniJobBase):
    """StockNewInitializer: Find new listed stock symbols

    Find new listed stock symbols from the daily listed stock prices. Then, create draft info data in the stock
    database. Then, the crawler will collect info about these new stocks.
    """

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        is_trading_date = MarketdbClient().check_calendar(datetime_obj)
        if not is_trading_date:
            logger.info(f"StockNewInitializer: No trading today: {input_date}")
            return True

        df = self.load_price_intraday_data(input_date)
        if df.empty:
            logger.warning("StockNewInitializer: load_price_data no data")
            return False

        df["exchange"] = df["exchange"].apply(lambda x: x.lower() if x else x)
        df["type"] = df["type"].apply(lambda x: x.lower() if x else x)

        # Indexing new stocks into db
        stock_df = df[df.type == "stock"].apply(
            lambda row: {
                "symbol": row["symbol"],
                "exchange": row["exchange"],
                "type": row["type"],
                "exchange_status": row["exchange_status"],
            },
            axis=1,
        )

        if not stock_df.empty:
            self.save_stock_symbols(stock_df)
            logger.info(
                "StockNewInitializer: Stock price data is successfully executed"
            )
        else:
            logger.warning("StockNewInitializer: no stock price data is loaded")

        # Indexing new etf into db
        etf_df = df[df.type == "etf"].apply(
            lambda row: {
                "symbol": row["symbol"],
                "exchange": row["exchange"],
                "type": row["type"],
                "exchange_status": row["exchange_status"],
            },
            axis=1,
        )

        if not etf_df.empty:
            self.save_etf_symbols(etf_df)
            logger.info("StockNewInitializer: ETF price data is successfully executed")
        else:
            logger.warning("StockNewInitializer: no etf price data is loaded")

        return True

    def load_price_intraday_data(self, input_date) -> DataFrame:
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

        # make sure datetime is tz-aware datetime
        stock_datetime = ensure_tzaware_datetime(row["timestamp"], tz=VN_TIMEZONE)

        # set the opened trading date
        stock_datetime = stock_datetime.replace(hour=9, minute=0, second=0)
        stock_date = stock_datetime.date()
        standardized_exchange = row["exchange"].lower()

        return {
            "symbol": row["symbol"],
            "date": stock_date,
            "exchange": standardized_exchange,
            "type": self._get_type(row.get("type")),
            "datetime": stock_datetime,
            "price": row.get("reference"),
            "reference": row.get("reference"),
            "ceiling": row.get("ceiling"),
            "floor": row.get("floor"),
            "exchange_status": 1002,  # LISTED
            "volume": 0,
            "fb_volume": 0,
            "fs_volume": 0,
            "foreign_room": 0,  # not open time for trading then volume = 0
            "open": None,
            "high": None,
            "low": None,
            "close": None,
        }

    def save_stock_symbols(self, items):
        stock_values = self.marketdb_client.get_stock_items()
        stocks = {}
        for stock in stock_values:
            stocks[stock["symbol"]] = stock["exchange"]

        # convert series of dicts to list of dicts
        items = items.tolist()
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="core.Stock",
                key_fields=["symbol"],
                payload=items,
            )
            if not success:
                logger.error(f"Error indexing: {response}")
            else:
                logger.debug(f"Indexing listed stocks response: {response}")
        except Exception as ex:
            logger.error(f"Error indexing listed stocks: {ex}")

        # remove stock from the stocks to be updated
        for item in items:
            stocks.pop(item["symbol"], None)

        # update delisted stocks
        delisted_df = pd.DataFrame.from_dict(stock_values)
        delisted_df = delisted_df[delisted_df["symbol"].isin(stocks)]
        delisted_df = delisted_df.drop(columns=["created", "modified"], axis=1)
        delisted_df.rename(
            columns={
                "industry": "industry_id",
                "super_sector": "super_sector_id",
                "sector": "sector_id",
                "sub_sector": "sub_sector_id",
            },
            inplace=True,
        )
        delisted_df = delisted_df.fillna('')

        delisted_df["exchange_status"] = 1003  # DELISTED
        delisted_df["industry_id"] = delisted_df["industry_id"].astype(int, errors='ignore')
        delisted_df["super_sector_id"] = delisted_df["super_sector_id"].astype(int, errors='ignore')
        delisted_df["sector_id"] = delisted_df["sector_id"].astype(int, errors='ignore')
        delisted_df["sub_sector_id"] = delisted_df["sub_sector_id"].astype(int, errors='ignore')

        # indexing to db
        delisted_stock_values = delisted_df.to_dict("records")
        try:
            if delisted_stock_values:
                success, response = self.marketdb_client.index_to_db_bulk(
                    model_name="core.Stock",
                    key_fields=["symbol"],
                    payload=delisted_stock_values,
                )
                if not success:
                    logger.error(f"Error indexing delisted stocks: {response}")

        except Exception as ex:
            logger.error(f"Error indexing delisted stocks: {ex}")

    def save_etf_symbols(self, items):
        etf_values = self.marketdb_client.get_etf_items()
        etfs = {}
        for etf in etf_values:
            etfs[etf["symbol"]] = etf["exchange"]

        # convert series of dicts to list of dicts
        items = items.tolist()
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="ETF",
                key_fields=["symbol"],
                payload=items,
            )
            if not success:
                logger.error(f"Error indexing listed etfs: {response}")
            else:
                logger.debug(f"Indexing response listed etfs: {response}")
        except Exception as ex:
            logger.error(f"Error indexing: {ex}")

        # remove stock from the stocks to be updated
        for item in items:
            etfs.pop(item["symbol"], None)

        # update delisted ETFs
        delisted_etf_df = pd.DataFrame.from_dict(etf_values)
        delisted_etf_df = delisted_etf_df[delisted_etf_df["symbol"].isin(etfs)]
        delisted_etf_df = delisted_etf_df.drop(
            columns=["created", "modified"], axis=1
        )
        delisted_etf_df["exchange_status"] = 1003  # DELISTED

        # indexing to db
        delisted_etf_values = delisted_etf_df.to_dict("records")
        try:
            if delisted_etf_values:
                success, response = self.marketdb_client.index_to_db_bulk(
                    model_name="ETF",
                    key_fields=["symbol"],
                    payload=delisted_etf_values,
                )
                if not success:
                    logger.error(f"Error indexing delisted etfs: {response}")

        except Exception as ex:
            logger.error(f"Error indexing delisted etfs: {ex}")
