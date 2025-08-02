import pandas as pd
import pytz

from dateutil import parser
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class MutualFundNAVDailyETL(MiniJobBase):
    """
    This is indexing the daily NAV
    """

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    bucket_name: str = ""

    def __init__(self, sampling_ratio: float = 1.0):
        super().__init__()

        self.sampling_ratio = sampling_ratio
        self.new_lines = False
        self.bucket_name = Config().get_bucket_name()
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.load(
            input_date=input_date,
            bucket_name=self.bucket_name,
            base_path="crawler/mutual_fund_daily_nav",
        )

        if not self.data_frame.empty:
            items = self.data_frame.apply(self.transform_row, axis=1)
            items = items.dropna().to_list()
            if len(items) == 0:
                logger.warning(f"Error: no data is loaded for {input_date}")
                return False

            self.do_indexing_fund_nav_daily(items)
            self.do_indexing_fund_nav_index(items)

            logger.info("MutualFundNAVDailyETL is successfully executed.")
            return True

        logger.warning(f"Error: no data is loaded for {input_date}")
        return False

    def transform_row(self, row: dict) -> dict:
        row = self.fill_row_na(row)

        fund_datetime = row.get("datetime")
        if not fund_datetime:
            raise Exception("datetime is missing")

        if isinstance(fund_datetime, str):
            fund_datetime = parser.parse(row.get("datetime"))

        # make sure datetime is tz-aware datetime
        timezone = pytz.timezone(VN_TIMEZONE)
        fund_datetime = timezone.localize(fund_datetime)
        fund_date = fund_datetime.strftime("%Y-%m-%d")
        symbol = row.get("symbol")
        if not symbol:
            # skip the row if symbol is missing
            return None

        return {
            "symbol": symbol,
            "date": fund_date,
            "datetime": fund_datetime,
            "nav": row.get("nav"),
        }

    def do_indexing_fund_nav_daily(self, items: list):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="MutualFundNavDaily",
                key_fields=["symbol", "date"],
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

    def do_indexing_fund_nav_index(self, items: list):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="MutualFundNavIndex",
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
