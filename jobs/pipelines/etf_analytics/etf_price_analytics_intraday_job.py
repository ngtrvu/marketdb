import pandas as pd

from pandas import DataFrame

from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
)
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config
from pipelines.stock_prices.utils import ChangeUtils
from common.mdb.job import MarketDbJob


class ETFPriceAnalyticsIntradayJob(MarketDbJob):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    change_utils: ChangeUtils
    bucket_name: str

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.change_utils = ChangeUtils()
        self.bucket_name = Config().get_bucket_name()

        super().__init__()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(
                f"ETFPriceAnalyticsIntradayJob: No trading today {input_date}..."
            )
            return True

        stock_analytics_df = self.load(
            input_date=input_date,
            bucket_name=self.bucket_name,
            base_path="marketdb/etf_price_chart",
            file_name_prefix="etf_price_chart.json",
        )
        if stock_analytics_df.empty:
            logger.warning(
                "ETFPriceAnalyticsIntradayJob Error: no stock price analytics is loaded."
            )
            return False

        intraday_price_df = self.load(
            input_date=input_date,
            bucket_name=self.bucket_name,
            base_path="marketdb/stock_price_intraday",
            file_name_prefix="stock_price_ohlc.json",
        )
        if intraday_price_df.empty:
            logger.warning(
                "ETFPriceAnalyticsIntradayJob Error: no intraday price is loaded."
            )
            return False

        # Stock Price Analytics (% Change)
        intraday_price_df = intraday_price_df[intraday_price_df["type"] == "ETF"][
            ["symbol", "price", "volume"]
        ]
        intraday_price_df.set_index("symbol")

        stock_analytics_df = stock_analytics_df.drop(columns=["price"])
        self.data_frame = pd.merge(stock_analytics_df, intraday_price_df, on=["symbol"])
        self.data_frame = self.data_frame.apply(
            lambda row: self.compute_analytics(row["price"], row), axis=1
        )

        self.data_frame["date"] = self.data_frame["date"].dt.date
        self.data_frame["datetime"] = (
            self.data_frame["datetime"].dt.tz_localize("UTC").dt.tz_convert(VN_TIMEZONE)
        )
        self.data_frame["total_trading_value"] = (
            self.data_frame["volume"] * self.data_frame["price"]
        )

        computed_analytics = self.data_frame.to_dict("records")

        # convert NaN to None value for indexing
        for analytics_data in computed_analytics:
            for key, val in analytics_data.items():
                if self.is_nan(val):
                    analytics_data[key] = None

        success, response = self.do_indexing(items=computed_analytics)

        if success:
            logger.info("ETFPriceAnalyticsIntradayJob is successfully executed!")
            return True
        else:
            logger.error(
                f"ETFPriceAnalyticsIntradayJob indexing failed! Response: {response}"
            )
            return False

    def is_nan(self, val):
        return val != val

    def compute_analytics(
        self, current_price: float, stock_analytics_row: dict
    ) -> dict:
        stock_analytics_row["change_percentage_1d"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_1d"]
            )
        )
        stock_analytics_row["change_percentage_1w"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_1w"]
            )
        )
        stock_analytics_row["change_percentage_1m"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_1m"]
            )
        )
        stock_analytics_row["change_percentage_3m"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_3m"]
            )
        )
        stock_analytics_row["change_percentage_6m"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_6m"]
            )
        )
        stock_analytics_row["change_percentage_1y"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_1y"]
            )
        )
        stock_analytics_row["change_percentage_3y"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_3y"]
            )
        )
        stock_analytics_row["change_percentage_5y"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_5y"]
            )
        )
        stock_analytics_row["change_percentage_ytd"] = (
            self.change_utils.compute_change_percentage(
                current_price, stock_analytics_row["price_ytd"]
            )
        )

        return stock_analytics_row

    def do_indexing(self, items: list[dict]):
        try:
            success, response = MarketdbClient().index_to_db_bulk(
                model_name="ETFPriceChart", key_fields=["symbol"], payload=items
            )
            return success, response
        except Exception as ex:
            logger.error(f"Indexing ETFPriceAnalyticsIntradayJob error: {ex}.")
            return False, response
