import pandas as pd

from datetime import datetime, timedelta
from pandas import DataFrame

from joblib import Parallel, delayed
from common.tinydwh.base import MiniJobBase
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    get_datetime_now,
    str_to_datetime,
)
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class StockPriceAnalyticsJob(MiniJobBase):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    data_type: str
    analytics_rows: list = []
    chart_rows: list = []
    parallel: int = 1
    marketdb_client: MarketdbClient = None
    bucket_name: str
    selected_fields = ["symbol", "date", "close", "volume"]

    def __init__(self, sampling_ratio: float = 1.0):
        self.error_message = None
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()
        self.analytics_rows = []
        self.chart_rows = []
        self.bucket_name = Config().get_bucket_name()

    def pipeline(
        self,
        input_date: str = None,
        type: str = None,
        data_type: str = None,
    ):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(f"StockPriceAnalyticsJob: No trading today {input_date}...")
            return True

        self.intraday_df = self.load_daily_stock_prices(date_str=input_date)
        if self.intraday_df.empty:
            logger.warning("StockPriceAnalyticsJob: No intraday data...")
            return False

        self.data_type = data_type
        # load end of day stock price OHLC on the previous trading date
        yesterday_input_date = self.get_previous_trading_date_str(date_str=input_date)
        self.load(
            bucket_name=self.bucket_name,
            base_path="marketdb/stock_price_ohlc_bulk_v3",
            input_date=yesterday_input_date,
            file_name_prefix="stock_price_bulk.json",
        )

        if self.data_frame.empty:
            logger.warning("StockPriceAnalyticsJob: No historical data...")
            return False
        logger.info(
            f"StockPriceAnalyticsJob: {self.data_frame.shape} records loaded..."
        )

        self.data_frame = self.data_frame[self.selected_fields]
        self.data_frame = self.data_frame.sort_values(
            by=["date", "symbol"], ascending=False
        )

        symbols: list = []

        # load all stocks
        if not type or type.lower() == "stock":
            symbols += self.marketdb_client.get_stock_symbols()

        current_date = str_to_datetime(
            input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

        # remove duplicates
        symbols = list(set(symbols))
        symbols = sorted(symbols)

        logger.info(f"Start computing for {len(symbols)} symbols...")
        Parallel(n_jobs=self.parallel)(
            delayed(self.compute)(symbol, current_date) for symbol in symbols
        )

        logger.info(f"StockPriceAnalyticsJob: Computed!")

        # indexing to db
        if not self.data_type or self.data_type == "analytics":
            logger.info(f"Start indexing for analytics...")
            success, response = self.indexing_analytics(items=self.analytics_rows)
            if success:
                logger.info(f"Indexed analytics: {response['total']} items!")
            else:
                logger.error(f"Indexing analytics Failed! Response: {response}")
                return False

        if not self.data_type or self.data_type == "charts":
            logger.info(f"Start indexing for charts...")
            success, response = self.indexing_charts(items=self.chart_rows)
            if success:
                logger.info(f"Indexed charts: {response['total']} items!")
            else:
                logger.error(f"Indexing charts Failed! Response: {response}")
                return False

        logger.info(f"StockPriceAnalyticsJob: Done!")
        return True

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(
            input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

    def get_yesterday_str(self, input_date: str) -> str:
        datetime_obj = str_to_datetime(
            input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        return get_date_str(
            datetime_obj - timedelta(days=1), date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

    def get_previous_trading_date_str(self, date_str: str) -> str:
        """Get the most recent previous trading date."""
        most_recent_trading_date = self.get_yesterday_str(input_date=date_str)

        while not self.is_trading_date(date_str=most_recent_trading_date):
            most_recent_trading_date = self.get_yesterday_str(
                input_date=most_recent_trading_date
            )

        return most_recent_trading_date

    def load_daily_stock_prices(self, date_str: str):
        self.new_lines = True
        df = self.load(
            bucket_name=self.bucket_name,
            base_path="marketdb/stock_price_intraday",
            input_date=date_str,
            file_name_prefix="stock_price_ohlc.json",
        )
        if not df.empty:
            logger.info(f"Load daily trading data on {date_str} successfully...")
            if "date" not in df.columns:
                df = self.convert_timestamps_to_date_strs(df)

            return df

        return pd.DataFrame()

    def convert_timestamps_to_date_strs(self, df: pd.DataFrame) -> pd.DataFrame:
        # convert integer timestamp to datetime
        df["date"] = pd.to_datetime(df["timestamp"], unit="s")
        # convert UTC to Vietnam timezone
        df["date"] = df["date"].dt.tz_localize("UTC").dt.tz_convert(VN_TIMEZONE)
        # format datetime as date string
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        return df

    def is_nan(self, value):
        return value != value

    def compute(self, symbol: str, current_date: datetime):
        df = self.data_frame[self.data_frame["symbol"] == symbol]
        intraday_df = self.intraday_df[self.intraday_df["symbol"] == symbol]

        if df.empty or intraday_df.empty:
            return False

        item_1d, chart_1d = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_1D, datetime_obj=current_date
        )
        item_1w, chart_1w = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_1W, datetime_obj=current_date
        )
        item_1m, chart_1m = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_1M, datetime_obj=current_date
        )
        item_3m, chart_3m = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_3M, datetime_obj=current_date
        )
        item_6m, chart_6m = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_6M, datetime_obj=current_date
        )
        item_1y, chart_1y = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_1Y, datetime_obj=current_date
        )
        item_3y, chart_3y = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_3Y, datetime_obj=current_date
        )
        item_5y, chart_5y = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_5Y, datetime_obj=current_date
        )
        item_ytd, chart_ytd = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_YTD, datetime_obj=current_date
        )
        reference_price = intraday_df.loc[intraday_df["symbol"] == symbol, "reference"].iloc[0]
        analytics_row = {
            "symbol": symbol,
            "reference": float(reference_price),
            "date": current_date.date(),
            "datetime": get_datetime_now(tz=VN_TIMEZONE),
            "price_1d": float(item_1d.close) if not item_1d.empty else None,
            "price_1w": float(item_1w.close) if not item_1w.empty else None,
            "price_1m": float(item_1m.close) if not item_1m.empty else None,
            "price_3m": float(item_3m.close) if not item_3m.empty else None,
            "price_6m": float(item_6m.close) if not item_6m.empty else None,
            "price_1y": float(item_1y.close) if not item_1y.empty else None,
            "price_3y": float(item_3y.close) if not item_3y.empty else None,
            "price_5y": float(item_5y.close) if not item_5y.empty else None,
            "price_ytd": float(item_ytd.close) if not item_ytd.empty else None,
            "volume_1d": float(item_1d.volume) if not item_1d.empty else None,
            "volume_1w": float(item_1w.volume) if not item_1w.empty else None,
            "volume_1m": float(item_1m.volume) if not item_1m.empty else None,
            "volume_3m": float(item_3m.volume) if not item_3m.empty else None,
            "volume_6m": float(item_6m.volume) if not item_6m.empty else None,
            "volume_1y": float(item_1y.volume) if not item_1y.empty else None,
            "volume_3y": float(item_3y.volume) if not item_3y.empty else None,
            "volume_5y": float(item_5y.volume) if not item_5y.empty else None,
        }
        for key, value in analytics_row.items():
            if self.is_nan(value):
                analytics_row[key] = None

        chart_row = {
            "symbol": symbol,
            "datetime": get_datetime_now(tz=VN_TIMEZONE),
            "movement_1w": chart_1w,
            "movement_1m": chart_1m,
            "movement_3m": chart_3m,
            "movement_6m": chart_6m,
            "movement_1y": chart_1y,
            "movement_3y": chart_3y,
            "movement_5y": chart_5y,
            'movement_ytd': chart_ytd,
        }
        for key, value in chart_row.items():
            if self.is_nan(value):
                chart_row[key] = None

        self.analytics_rows.append(analytics_row)
        self.chart_rows.append(chart_row)
        return True

    def get_by_date_range(
        self, df: pd.DataFrame, date_range: str, datetime_obj: datetime
    ) -> (pd.Series, list):
        from_date, to_date = DateRangeUtils().get_date_range_as_string(
            date_range=date_range,
            to_date=datetime_obj.date(),
            date_format="%Y-%m-%d",
            tz=VN_TIMEZONE,
        )

        date_range_df = df[df["date"] <= from_date]
        chart_df = df[["date", "close"]][df["date"] >= from_date]
        chart_data = chart_df.sort_values(by=["date"], ascending=True).to_dict(
            orient="records"
        )
        if not date_range_df.empty:
            return date_range_df.iloc[0], self.__build_chart(chart_data or [])
        return pd.Series([], dtype="object"), []

    def __build_chart(self, chart_data: list) -> list[dict]:
        chart_items = []
        for item in chart_data:
            if not self.is_nan(item["close"]) and not self.is_nan(item["date"]):
                avt = {
                    # "o": None,
                    # "h": None,
                    # "l": None,
                    "c": item["close"],
                    "t": item["date"] if isinstance(item["date"], str) else item["date"].timestamp(),
                    # "v": item['volume'],
                }
                chart_items.append(avt)
        return chart_items

    def indexing_analytics(self, items: list[dict]):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="StockPriceAnalytics", key_fields=["symbol"], payload=items
            )
            return success, response
        except Exception as ex:
            logger.error(f"Indexing analytics error, {ex}.")
            return False, None

    def indexing_charts(self, items: list[dict]):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="StockPriceChart", key_fields=["symbol"], payload=items, batch_size=100
            )
            return success, response
        except Exception as ex:
            logger.error(f"Indexing chart error, {ex}.")
            return False, None
