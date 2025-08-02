import pandas as pd
from pandas import DataFrame
from datetime import timedelta

from utils.logger import logger
from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
    ensure_tzaware_datetime,
)
from common.mdb.trading_calendar import TradingCalendar
from config import Config


class MarketIndexBulkTransformV1(MiniJobBase, TradingCalendar):
    """Market Index Bulk Transform

    Load data from GCS (cafef or iboard), then transform it to the format of Market Index OHLC Bulk.
    """

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    symbol: str
    exchange: str

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.data_frame: DataFrame = pd.DataFrame()

        super().__init__()

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        input_date = self.get_previous_trading_date(input_date)
        if not self.is_trading_date(input_date):
            logger.info(f"MarketIndexBulkTransform: No trading today: {input_date}")
            return True
        self.data_frame = self.load_cafef_csv(
            input_date=input_date, base_path=f"crawler/cafef_market_index_bulk"
        )

        if self.data_frame.empty:
            logger.error(f"MarketIndexBulkTransform Error: no csv data is loaded.")
            return False

        gcs_path = (
            f"marketdb/market_index_ohlc_bulk/{input_date}/market_index_ohlc_bulk.json"
        )
        self.export_to_gcs(
            df=self.data_frame, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
        )

        logger.info(f"MarketIndexBulkTransform is successfully executed.")
        return True

    def load_cafef_csv(self, input_date: str, base_path: str = ""):
        date_obj = str_to_datetime(input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        cafef_date_dir = get_date_str(date_obj, date_format="%d.%m.%Y", tz=VN_TIMEZONE)

        gcs_path = f"gcs://{Config.BUCKET_NAME}/{base_path}/CafeF.INDEX.Upto{cafef_date_dir}.csv"
        logger.info(f"Loading csv data from {gcs_path}")

        try:
            df = pd.read_csv(gcs_path)
        except Exception as ex:
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
        df["open"] = df["open"]
        df["high"] = df["high"]
        df["low"] = df["low"]
        df["close"] = df["close"]

        return df
