import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.data import is_nan
from common.tinydwh.datetime_util import (
    get_date_str,
    str_to_datetime,
    VN_TIMEZONE,
)
from utils.logger import logger
from common.tinydwh.storage.connector import GCS
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class StockEventLogETL(MiniJobBase):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = False
        self.marketdb_client = MarketdbClient()

        super().__init__()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.load(
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="crawler/iboard-corporate-actions",
        )

        updated = 0
        if not self.data_frame.empty:
            index_df = self.data_frame
            index_df = index_df[~index_df["symbol"].isnull()]
            index_df = index_df[~index_df["event_type"].isnull()]
            index_df = index_df[~index_df["public_date"].isnull()]
            uploaded = self.do_stock_event_log(index_df=index_df, input_date=input_date)
            updated = self.do_indexing(index_df)

            logger.info(
                f"StockEventLogETL is successfully,uploaded {uploaded}, index executed: {updated}"
            )
        else:
            logger.warning(f"No stock event on {input_date}")

        return updated

    def do_stock_event_log(self, index_df: DataFrame, input_date: str):
        if index_df.empty:
            return False
        input_date_obj = str_to_datetime(
            input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

        gcs = GCS()
        symbols = index_df["symbol"].unique()
        public_dates = index_df["public_date"].unique()

        dataset_name = "stock_event_log"
        namespace = "marketdb"

        count_upload = 0
        public_date_objs = []
        for public_date in public_dates:
            public_date_obj = str_to_datetime(
                public_date, date_format="%Y-%m-%d", tz=VN_TIMEZONE
            )

            public_date_objs.append(public_date_obj)
            public_date_gcs = get_date_str(
                public_date_obj, date_format="%Y/%m/%d", tz=VN_TIMEZONE
            )

            tmp_df = index_df[index_df["public_date"] == public_date]
            if tmp_df.empty:
                continue

            symbol_data = tmp_df.to_json(orient="records", lines=True)
            gcs_path = f"{namespace}/{dataset_name}/{public_date_gcs}/stock_events.json"
            logger.info(f"Upload {gcs_path} to GCS...")
            is_uploaded = gcs.upload_dict(
                dict_json=symbol_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
            )
            count_upload += 1 if is_uploaded else 0

        # using nearest exright date to cleanup all future event and remove
        public_date_nearest = min(public_date_objs)
        current_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        current_date_obj = str_to_datetime(
            current_date, date_format="%Y-%m-%d", tz=VN_TIMEZONE
        )

        return count_upload

    def do_indexing(self, df: DataFrame):

        # FLUSH ALL EVENT HAVE THAT PUBLISH DATE
        public_dates = df["public_date"].unique()
        symbols = df["symbol"].unique()

        self.marketdb_client.delete_stock_events(
            symbols=symbols, public_dates=public_dates
        )

        items = df.to_dict(orient="records")
        count = 0
        for item in items:
            symbol = item.get("symbol")
            public_date = item.get("public_date")
            name = item.get("name")
            event_type = item.get("event_type")
            dividend_type = item.get("dividend_type")
            exright_date = item.get("exright_date")
            record_date = item.get("record_date")
            issue_date = item.get("issue_date")
            value = item.get("value")
            ratio = item.get("ratio")

            payload = {
                "symbol": symbol,
                "title": item.get("title"),
                "description": item.get("description"),
                "name": name,
                "public_date": public_date if not is_nan(public_date) else None,
                "exright_date": exright_date if not is_nan(exright_date) else None,
                "record_date": record_date if not is_nan(record_date) else None,
                "issue_date": issue_date if not is_nan(issue_date) else None,
                "value": item.get("value"),
                "ratio": item.get("ratio"),
                "dividend_type": item.get("dividend_type"),
                "event_type": item.get("event_type"),
            }

            if symbol and event_type:
                success, response = self.marketdb_client.index_to_db_bulk(
                    model_name="StockEventLog",
                    key_fields=[
                        "symbol",
                        "public_date",
                        "record_date",
                        "issue_date",
                        "dividend_type",
                        "event_type",
                        "value",
                        "ratio",
                    ],
                    payload=[payload],
                )
                if not success:
                    logger.error(f"Error indexing: {response}")
                    return False

        return count
