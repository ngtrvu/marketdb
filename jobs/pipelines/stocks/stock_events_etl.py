import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.data import is_nan
from common.tinydwh.datetime_util import get_date_str
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class StockEventETL(MiniJobBase):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    marketdb_client: MarketdbClient = None

    def __init__(
        self, marketdb_client: MarketdbClient = None, sampling_ratio: float = 1.0
    ):
        self.sampling_ratio = sampling_ratio
        self.new_lines = False
        if not marketdb_client:
            self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz="Asia/Ho_Chi_Minh")

        self.load(
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="crawler/stock/corporate-events/ssi-iboard",
        )
        df = self.data_frame.apply(self.transform_row, axis=1)
        updated = 0

        if not df.empty:
            index_df = pd.DataFrame(df.tolist())
            index_df = index_df[~index_df["symbol"].isnull()]
            index_df = index_df[~index_df["event_type"].isnull()]
            index_df = index_df[~index_df["public_date"].isnull()]
            updated = self.do_indexing(index_df)

            logger.info(f"StockEventETL is successfully executed: {updated}")
        else:
            logger.warning("No data")

        return updated

    def transform_row(self, row: dict) -> dict:
        exright_date = (
            row.get("exrightdate").split(" ")[0] if row.get("exrightdate") else None
        )
        record_date = (
            row.get("recorddate").split(" ")[0] if row.get("recorddate") else None
        )
        issue_date = (
            row.get("issuedate").split(" ")[0] if row.get("issuedate") else None
        )
        public_date = (
            row.get("publicdate").split(" ")[0] if row.get("publicdate") else None
        )
        event_name = row.get("eventname")
        dividend_type = ""
        event_type = ""
        if event_name == "Trả cổ tức bằng tiền mặt":
            dividend_type = "cash"
            event_type = "dividend"
        elif event_name == "Trả cổ tức bằng cổ phiếu":
            dividend_type = "stock"
            event_type = "dividend"
        elif event_name == "Phát hành cổ phiếu":
            dividend_type = "stock"
            event_type = "issue"

        if not dividend_type or not event_type:
            return {}

        return {
            "symbol": row.get("symbol"),
            "name": event_name,
            "title": row.get("eventtitle"),
            "description": row.get("eventdescription"),
            "exright_date": exright_date,
            "record_date": record_date,
            "issue_date": issue_date,
            "public_date": public_date,
            "value": float(row.get("value")),
            "ratio": float(row.get("ratio")),
            "dividend_type": dividend_type,
            "event_type": event_type,
        }

    def do_indexing(self, df: DataFrame):
        items = df.to_dict(orient="records")
        count = 0
        for item in items:
            symbol = item.get("symbol")
            public_date = item.get("public_date")
            name = item.get("name")
            event_type = item.get("event_type")
            exright_date = item.get("exright_date")
            record_date = item.get("record_date")
            issue_date = item.get("issue_date")

            payload = {
                "title": item.get("title"),
                "description": item.get("description"),
                "exright_date": exright_date if not is_nan(exright_date) else None,
                "record_date": record_date if not is_nan(record_date) else None,
                "issue_date": issue_date if not is_nan(issue_date) else None,
                "value": item.get("value"),
                "ratio": item.get("ratio"),
                "dividend_type": item.get("dividend_type"),
                "event_type": item.get("event_type"),
            }
            if symbol and event_type:
                success, response = self.marketdb_client.update_or_create(
                    model_name="StockEvent",
                    key_name="symbol",
                    key_value=symbol,
                    payload=payload,
                )
                if not success:
                    logger.error(f"StockEvent update item error: {response}")
                else:
                    count += 1

        return count
