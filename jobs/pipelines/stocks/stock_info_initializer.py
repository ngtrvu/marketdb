import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.data import is_nan
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


class StockInfoInitializer(MiniJobBase):
    """StockInfoInitializer: Load new stock info from the crawler's data to the db"""

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

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
        is_trading_date = MarketdbClient().check_calendar(datetime_obj)
        if not is_trading_date:
            logger.info(f"StockInfoInitializer: No trading today: {input_date}")
            return True

        items = self.load_new_stock_profile(
            base_path="crawler/iboard_stock_profile", input_date=input_date
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

            return df.tolist()
        else:
            logger.warning("No stock profile data")

    def transform_industry_row(self, row: dict) -> dict:
        subsectorcode = row.get("subsectorcode")
        sectorcode = subsectorcode[0:3] + "0"
        supersectorcode = subsectorcode[0:2] + "00"
        industrycode = subsectorcode[0:1] + "000"
        industrycode = "0001" if industrycode == "0000" else industrycode

        return {
            "symbol": row.get("symbol"),
            "subsectorcode": subsectorcode,
            "subsector": row.get("subsector"),
            "subsector_id": int("1{0}".format(subsectorcode)),
            "sectorcode": sectorcode,
            "sector": row.get("sector"),
            "sector_id": int("1{0}".format(sectorcode)),
            "supersectorcode": supersectorcode,
            "supersector": row.get("supersector"),
            "supersector_id": int("1{0}".format(supersectorcode)),
            "industrycode": industrycode,
            "industry": row.get("industryname"),
            "industry_id": int("1{0}".format(industrycode)),
        }

    def transform_row(self, row: dict) -> dict:
        industry_id = None
        super_sector_id = None
        sector_id = None
        sub_sector_id = None

        subsectorcode = row.get("subsectorcode", "")
        subsector = row.get("subsector", "")

        if subsectorcode and subsector and isinstance(subsectorcode, str):
            industry_icb_code = subsectorcode[0:1] + "000"
            industry_icb_code = (
                "0001" if industry_icb_code == "0000" else industry_icb_code
            )
            industry_id = int("1{0}".format(industry_icb_code)) if industry_id else None

            super_sector_icb_code = subsectorcode[0:2] + "00"
            super_sector_id = (
                int("1{0}".format(super_sector_icb_code))
                if super_sector_icb_code
                else None
            )

            sector_icb_code = subsectorcode[0:3] + "0"
            sector_id = int("1{0}".format(sector_icb_code)) if sector_icb_code else None

            sub_sector_icb_code = subsectorcode
            sub_sector_id = (
                int("1{0}".format(sub_sector_icb_code)) if sub_sector_icb_code else None
            )

        symbol = row["symbol"]
        if symbol:
            return {
                "symbol": symbol,
                "name": row["companyname"],
                "exchange": row.get("exchange", "").strip().lower(),
                "industry_id": industry_id if not is_nan(industry_id) else None,
                "super_sector_id": (
                    super_sector_id if not is_nan(super_sector_id) else None
                ),
                "sector_id": sector_id if not is_nan(sector_id) else None,
                "sub_sector_id": sub_sector_id if not is_nan(sub_sector_id) else None,
                "outstanding_shares": float(row.get("sharesoutstanding")),
                "status": 1002,  # PUBLISHED
                "exchange_status": 1002,  # LISTED
                "currency": "VND",
            }

    def do_indexing(self, items: list):
        if not items:
            return False

        stock_values = self.marketdb_client.get_stock_items(["symbol"])
        stocks = {}
        for stock in stock_values:
            stocks[stock["symbol"]] = True

        for item in items:
            symbol = item.get("symbol")
            if symbol and symbol in stocks:
                # Stock.objects.update_or_create(symbol=symbol, defaults=item)
                success, response = self.marketdb_client.update_or_create(
                    model_name="StockEvent",
                    key_name="symbol",
                    key_value=symbol,
                    payload=item,
                )
                if not success:
                    logger.error(f"ETF update item error: {response}")

        return True
