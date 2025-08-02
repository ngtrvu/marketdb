import pandas as pd

from datetime import timedelta

from common.tinydwh.base import MiniJobBase
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    date_str_reformat,
    get_date_str,
    str_to_datetime,
)
from utils.logger import logger
from common.tinydwh.storage.connector import GCS
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class StockCorporateAction(MiniJobBase):
    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    new_lines = False

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        is_trading_date = MarketdbClient().check_calendar(datetime_obj)
        if not is_trading_date:
            logger.info(f"StockCorporateAction: No trading today: {input_date}")
            return True

        # Load stock events by public date in 1 year
        self.new_lines = True
        stock_event_df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_event_1y",
            input_date=input_date,
            file_name_prefix="by_public_date.json",
        )
        if stock_event_df.empty:
            logger.debug(
                f"StockCorporateAction: Stock events 1 year on {input_date} is empty..."
            )
            return False

        stock_event_df = stock_event_df[
            [
                "symbol",
                "name",
                "eventType",
                "exrightDate",
                "publicDate",
                "issueDate",
                "recordDate",
                "ratio",
                "value",
                "description",
            ]
        ]

        # extract stock corporate actions
        next_trading_date_str = self.get_next_trading_date_str(input_date)
        next_trading_date_reformatted_str = date_str_reformat(
            next_trading_date_str, date_format="%Y/%m/%d", to_date_format="%Y-%m-%d"
        )
        corporate_action_df = stock_event_df.query(
            "exrightDate == @next_trading_date_reformatted_str"
        )
        self.data_frame = corporate_action_df.sort_values(by=["symbol"])

        # export stock corporate action to GCS
        self.export(next_trading_date_str, self.data_frame)
        return True

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

    def get_tomorrow_str(self, input_date: str) -> str:
        datetime_obj = str_to_datetime(
            input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return get_date_str(
            datetime_obj + timedelta(days=1), date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

    def get_next_trading_date_str(self, date_str: str) -> str:
        next_trading_date = self.get_tomorrow_str(input_date=date_str)

        while not self.is_trading_date(date_str=next_trading_date):
            next_trading_date = self.get_tomorrow_str(input_date=next_trading_date)

        return next_trading_date

    def export(self, input_date: str, df: pd.DataFrame):
        gcs = GCS()

        namespace = "marketdb"
        dataset_name = "corporate_action"
        gcs_path = f"{namespace}/{dataset_name}/{input_date}/{dataset_name}.json"

        logger.info(f"Upload to GCS: {gcs_path} ...")
        json_data = df.to_json(orient="records", lines=True, force_ascii=False).encode(
            "utf-8"
        )
        gcs.upload_dict(
            dict_json=json_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
        )

    def load_backfill_dates(self, input_date: str, from_date: str):
        utils = DateRangeUtils()
        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        from_date, to_date = utils.get_date_range(
            date_range=utils.DATE_RANGE_YTD, to_date=datetime_obj
        )
        return utils.get_dates_by_range(
            from_date, to_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
