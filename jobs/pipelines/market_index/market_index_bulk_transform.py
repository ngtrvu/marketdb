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


class MarketIndexBulkTransform(MiniJobBase, TradingCalendar):
    """Market Index Bulk Transform

    Load data from GCS (exported from db), then transform it to the format of Market Index OHLC Bulk.
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

        # load data from GCS: get latest bulk data exported from db
        self.data_frame = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/market_index_daily",
            file_name_prefix="market_index_daily.json",
        )

        if self.data_frame.empty:
            logger.error("MarketIndexBulkTransform Error: no data is loaded.")
            return False

        self.data_frame = self.transform(self.data_frame)
        gcs_path = (
            f"marketdb/market_index_ohlc_bulk/{input_date}/market_index_ohlc_bulk.json"
        )
        self.export_to_gcs(
            df=self.data_frame, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
        )

        logger.info("MarketIndexBulkTransform is successfully executed.")
        return True

    def transform(self, df: DataFrame):
        # given the dataframe with the following columns (from db):
        # 1	id	int4	NO	NULL	NULL		NULL
        # 2	created	timestamptz	NO	NULL	NULL		NULL
        # 3	modified	timestamptz	NO	NULL	NULL		NULL
        # 4	symbol	varchar(50)	NO	NULL	NULL		NULL
        # 5	date	date	NO	NULL	NULL		NULL
        # 6	datetime	timestamptz	NO	NULL	NULL		NULL
        # 7	open	numeric(20,2)	YES	NULL	NULL		NULL
        # 8	high	numeric(20,2)	YES	NULL	NULL		NULL
        # 9	low	numeric(20,2)	YES	NULL	NULL		NULL
        # 10	close	numeric(20,2)	YES	NULL	NULL		NULL
        # 11	total_volume	numeric(20,2)	YES	NULL	NULL		NULL
        # 12	total_value	numeric(20,2)	NO	NULL	NULL		NULL

        # transform it to the following columns (to be used for bulk export):
        # symbol, date, open, high, low, close, volume

        # Convert date to proper format
        df["date"] = pd.to_datetime(df["date"]).dt.date

        df = df.rename(columns={
            "total_volume": "volume",
            "total_value": "value",
        })

        # Convert numeric columns to float
        numeric_columns = ["open", "high", "low", "close", "volume", "value"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Select only the required columns
        df = df[["symbol", "date", "open", "high", "low", "close", "volume", "value"]]

        return df
