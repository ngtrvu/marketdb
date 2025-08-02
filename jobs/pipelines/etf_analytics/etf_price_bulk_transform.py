import pandas as pd
from pandas import DataFrame
from datetime import timedelta

from common.tinydwh.base import MiniJobBase
from utils.logger import logger as logging
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
)
from common.mdb.client import MarketdbClient
from config import Config
from common.mdb.trading_calendar import TradingCalendar


class ETFPriceBulkTransform(MiniJobBase, TradingCalendar):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    symbol: str
    exchange: str

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.marketdb_client = MarketdbClient()

        super().__init__()

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        # load the bulk stock prices on previous trading date
        input_date = self.get_previous_trading_date(input_date=input_date)
        logging.info(
            f"ETFPriceBulkTransform: Loading bulk prices on {input_date}..."
        )

        self.data_frame = self._load_csv(
            input_date=input_date,
            exchange="HSX",
            base_path="crawler/cafef_stock_price_bulk",
        )

        if self.data_frame.empty:
            logging.error(
                f"ETFPriceBulkTransform Error: no data is loaded on {input_date}"
            )
            return False

        etf_symbols = self.get_all_etf_symbols()
        etf_df = self.data_frame[self.data_frame["symbol"].isin(etf_symbols)]
        gcs_path = f"marketdb/etf_price_ohlc_bulk/{input_date}/etf_price_bulk.json"
        self.export_to_gcs(df=etf_df, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path)
        logging.info(
            f"ETFPriceBulkTransform on {input_date} is successfully executed."
        )
        return True

    def get_all_etf_symbols(self) -> list:
        symbols = self.marketdb_client.get_etf_symbols()
        symbols = list(set(symbols))
        symbols = sorted(symbols)

        return symbols

    def _load_csv(self, input_date: str, exchange: str, base_path: str = ""):
        date_obj = str_to_datetime(input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        cafef_date_dir = get_date_str(date_obj, date_format="%d.%m.%Y", tz=VN_TIMEZONE)

        gcs_path = f"gcs://{Config.BUCKET_NAME}/{base_path}/CafeF.{exchange}.Upto{cafef_date_dir}.csv"
        logging.info(f"Loading csv data from {gcs_path}")

        try:
            df = pd.read_csv(gcs_path)
        except Exception as ex:
            logging.error(ex)
            return pd.DataFrame()

        df = df.rename(
            columns={
                "<Ticker>": "symbol",
                "<DTYYYYMMDD>": "date",
                "<Open>": "open",
                "<High>": "high",
                "<Low>": "low",
                "<Close>": "close",
                "<Volume>": "volume",
            }
        )
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.date
        df["open"] = df["open"] * 1000
        df["high"] = df["high"] * 1000
        df["low"] = df["low"] * 1000
        df["close"] = df["close"] * 1000
        return df
