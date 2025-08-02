from datetime import datetime

import pytz
import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    ensure_tzaware_datetime,
    get_date_str,
    str_to_datetime,
)
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class FearGreedIndexIndexerJob(MiniJobBase):
    """
    This is for one off load collection data from stockdb
    """

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    new_lines = False
    marketdb_client = MarketdbClient()

    def __init__(self, sampling_ratio: float = 1.0):
        self.input_date = None
        self.sampling_ratio = sampling_ratio

        super().__init__()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(f"FearGreedIndexIndexerJob: No trading today {input_date}...")
            return False

        self.input_date = input_date
        self.load(
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="analytics/fear_greed_index",
        )

        if self.data_frame.empty:
            logger.warning("FearGreedIndexIndexerJob: No data")
            return False

        items = self.data_frame.apply(self.transform_row, axis=1)
        self.do_indexing(items.to_list())
        return True

    def transform_row(self, row: dict):
        # make sure datetime is tz-aware datetime
        stock_date = ensure_tzaware_datetime(row["date"], tz=VN_TIMEZONE)
        # stock_datetime = ensure_tzaware_datetime(row["datetime"], tz=VN_TIMEZONE)
        current_time = datetime.now(pytz.timezone(VN_TIMEZONE)).time()
        # Combine the date from datetime_obj with the current time
        stock_datetime = pytz.timezone(VN_TIMEZONE).localize(
            datetime.combine(stock_date.date(), current_time)
        )
        market_indicators = row.get("market_indicators")
        fear_greed_score = row.get("fear_greed_score")

        if fear_greed_score and fear_greed_score.get("fear_greed_score"):
            return {
                "date": stock_date.date(),
                "datetime": stock_datetime,
                "score": fear_greed_score.get("fear_greed_score"),
                "price_breadth": fear_greed_score.get("price_breadth"),
                "price_breadth_diff": fear_greed_score.get("price_breadth_diff"),
                "market_index": market_indicators.get("market_index"),
                "market_index_1d": market_indicators.get("market_index_previous"),
                "market_index_diff": market_indicators.get("market_diff"),
                "rsi": market_indicators.get("market_rsi"),
                "price_strength": market_indicators.get("price_strength"),
                "momentum": market_indicators.get("momentum"),
                "momentum_diff": market_indicators.get("momentum_diff"),
                "volatility": market_indicators.get("market_volatility"),
                "volatility_sma": market_indicators.get("market_volatility_sma"),
            }

    def do_indexing(self, items: list):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="FearGreedIndexDaily",
                key_fields=["date"],
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

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return self.marketdb_client.check_calendar(datetime_obj=datetime_obj)

    def load_backfill_dates(self, to_date, from_date):
        range_utils = DateRangeUtils()
        # from_date, to_date = range_utils.get_date_range(date_range=range_utils.DATE_RANGE_DAYS, delta_days=n_day)
        from_date = str_to_datetime(
            input_str=from_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        to_date = str_to_datetime(
            input_str=to_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        dates = range_utils.get_dates_by_range(from_date, to_date)

        backfill_dates = [d.strftime("%Y/%m/%d") for d in dates]

        logger.info(f"All backfill dates {backfill_dates}")

        return backfill_dates
