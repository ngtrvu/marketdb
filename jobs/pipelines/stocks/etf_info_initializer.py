import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
)
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class ETFInfoInitializer(MiniJobBase):
    """ETFInfoInitializer: Load new etf info from the crawler's data to the db"""

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        is_trading_date = MarketdbClient().check_calendar(datetime_obj)
        if not is_trading_date:
            logger.info(f"ETFInfoInitializer: No trading today: {input_date}")
            return True

        items = self.load_new_stock_profile(
            base_path="crawler/iboard_etf_profile", input_date=input_date
        )
        self.do_indexing(items)
        return True

    def load_new_stock_profile(self, base_path, input_date):
        self.data_frame = self.load_json(
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path=base_path,
            nested_fields=["companyProfile", "companyStatistics"],
            key_field="symbol",
        )

        if not self.data_frame.empty:
            df = self.data_frame
            df = df[~df.symbol.isnull()]
            df = df.apply(self.transform_row, axis=1)

            logger.info("StockInfoETL is successfully executed")
            return df.tolist()
        else:
            logger.warning("No etf info data")

    def transform_row(self, row: dict) -> dict:
        symbol = row["symbol"]
        if symbol:
            return {
                "symbol": symbol,
                "name": row["companyname"],
                "description": row["companyprofile"],
                "exchange": row.get("exchange", "").strip().lower(),
                "outstanding_shares": float(row.get("sharesoutstanding")),
                "status": 1002,
                "exchange_status": 1002,  # LISTED
                "ipo_price": float(row.get("firstprice")),
                "ipo_shares": float(row.get("issueshare")),
                "currency": "VND",
            }

    def do_indexing(self, items: list):
        if not items:
            return

        etf_values = self.marketdb_client.get_etf_items(["symbol"])
        etfs = {}
        for etf in etf_values:
            etfs[etf["symbol"]] = True

        for item in items:
            symbol = item.get("symbol")
            if symbol and symbol in etfs:
                success, response = self.marketdb_client.update_or_create(
                    model_name="ETF",
                    key_name="symbol",
                    key_value=symbol,
                    payload=item,
                )

                if not success:
                    logger.error(f"ETF update item error: {response}")
