import pandas as pd

from datetime import datetime
from pandas import DataFrame
import numpy as np

from joblib import Parallel, delayed
from common.tinydwh.data_simplification import rdp_simplify
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    get_datetime_now,
    str_to_datetime,
)
from utils.logger import logger
from common.tinydwh.storage.connector import GCS
from common.mdb.client import (
    MarketdbClient,
)
from config import Config
from common.mdb.job import MarketDbJob


class ETFPriceAnalyticsJob(MarketDbJob):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    data_rows: list = []
    parallel: int = 1
    marketdb_client: MarketdbClient = None
    bucket_name: str
    selected_fields = ["symbol", "date", "close", "volume"]

    def __init__(self, sampling_ratio: float = 1.0):
        self.error_message = None
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()
        self.data_rows = []
        self.bucket_name = Config().get_bucket_name()
        self.intraday_df: pd.DataFrame = pd.DataFrame()

        super().__init__()

    def pipeline(
        self,
        input_date: str = None,
    ):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(f"ETFPriceAnalyticsJob: No trading today {input_date}...")
            return True

        self.intraday_df = self.load_daily_stock_prices(date_str=input_date)
        if self.intraday_df.empty:
            logger.warning("ETFPriceAnalyticsJob: No intraday data...")
            return False

        # load end of day stock price OHLC on the previous trading date
        yesterday_input_date = self.get_previous_trading_date_str(date_str=input_date)
        self.load(
            bucket_name=self.bucket_name,
            base_path="marketdb/etf_price_ohlc_bulk",
            input_date=yesterday_input_date,
            file_name_prefix="etf_price_bulk.json",
        )

        if self.data_frame.empty:
            logger.warning(
                f"ETFPriceAnalyticsJob: No historical data... {yesterday_input_date}"
            )
            return False

        logger.info(f"ETFPriceAnalyticsJob: {self.data_frame.shape} records loaded...")

        # sort by date descending
        self.data_frame = self.data_frame[self.selected_fields]
        self.data_frame = self.data_frame.sort_values(by=["date"], ascending=False)

        current_date = str_to_datetime(
            input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

        symbols: list = self.marketdb_client.get_etf_symbols()

        logger.info(f"Start computing for {len(symbols)} symbols...")
        Parallel(n_jobs=self.parallel)(
            delayed(self.compute)(symbol, current_date) for symbol in symbols
        )
        logger.info("ETFPriceAnalyticsJob: Computed!")

        self.export_to_gcs(df=pd.DataFrame(self.data_rows), input_date=input_date)

        logger.info("Start indexing for analytics...")
        success, response = self.indexing(items=self.data_rows)
        if success:
            logger.info(f"Indexed analytics: {response['total']} items!")
        else:
            logger.error(f"Indexing analytics Failed! Response: {response}")
            return False

        logger.info("ETFPriceAnalyticsJob: Done!")
        return True

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
        item_all, chart_all = self.get_by_date_range(
            df=df, date_range=DateRangeUtils.DATE_RANGE_ALL, datetime_obj=current_date
        )
        chart_all = self.simplify_chart_data(
            chart_all, epsilon=0.01
        )  # Simplify the chart data using RDP algorithm

        # build price values
        reference_price = float(
            intraday_df.loc[intraday_df["symbol"] == symbol, "reference"].iloc[0]
        )
        price = float(intraday_df.loc[intraday_df["symbol"] == symbol, "price"].iloc[0])
        item_1d_price = float(item_1d.close) if not item_1d.empty else None
        item_1w_price = float(item_1w.close) if not item_1w.empty else None
        item_1m_price = float(item_1m.close) if not item_1m.empty else None
        item_3m_price = float(item_3m.close) if not item_3m.empty else None
        item_6m_price = float(item_6m.close) if not item_6m.empty else None
        item_1y_price = float(item_1y.close) if not item_1y.empty else None
        item_3y_price = float(item_3y.close) if not item_3y.empty else None
        item_5y_price = float(item_5y.close) if not item_5y.empty else None
        item_ytd_price = float(item_ytd.close) if not item_ytd.empty else None
        item_all_price = float(item_all.close) if not item_all.empty else None

        # build row
        row = {
            "symbol": symbol,
            "reference": reference_price,
            "date": current_date.date(),
            "datetime": get_datetime_now(tz=VN_TIMEZONE),
            "price": price,
            "price_1d": item_1d_price,
            "price_1w": item_1w_price,
            "price_1m": item_1m_price,
            "price_3m": item_3m_price,
            "price_6m": item_6m_price,
            "price_1y": item_1y_price,
            "price_3y": item_3y_price,
            "price_5y": item_5y_price,
            "price_ytd": item_ytd_price,
            "price_inception_date": item_all_price,
            # "change_percentage_1d": self.get_percentage_change(item_1d_price, reference_price),
            # "change_percentage_1w": self.get_percentage_change(item_1w_price, reference_price),
            # "change_percentage_1m": self.get_percentage_change(item_1m_price, reference_price),
            # "change_percentage_3m": self.get_percentage_change(item_3m_price, reference_price),
            # "change_percentage_6m": self.get_percentage_change(item_6m_price, reference_price),
            # "change_percentage_1y": self.get_percentage_change(item_1y_price, reference_price),
            # "change_percentage_3y": self.get_percentage_change(item_3y_price, reference_price),
            # "change_percentage_5y": self.get_percentage_change(item_5y_price, reference_price),
            # "change_percentage_ytd": self.get_percentage_change(item_ytd_price, reference_price),
            "volume_1d": float(item_1d.volume) if not item_1d.empty else None,
            "volume_1w": float(item_1w.volume) if not item_1w.empty else None,
            "volume_1m": float(item_1m.volume) if not item_1m.empty else None,
            "volume_3m": float(item_3m.volume) if not item_3m.empty else None,
            "volume_6m": float(item_6m.volume) if not item_6m.empty else None,
            "volume_1y": float(item_1y.volume) if not item_1y.empty else None,
            "volume_3y": float(item_3y.volume) if not item_3y.empty else None,
            "volume_5y": float(item_5y.volume) if not item_5y.empty else None,
            "volume_all": float(item_all.volume) if not item_all.empty else None,
            "movement_1w": chart_1w,
            "movement_1m": chart_1m,
            "movement_3m": chart_3m,
            "movement_6m": chart_6m,
            "movement_1y": chart_1y,
            "movement_3y": chart_3y,
            "movement_5y": chart_5y,
            "movement_ytd": chart_ytd,
            "movement_all": chart_all,
        }

        for key, value in row.items():
            if self.is_nan(value):
                row[key] = None

        self.data_rows.append(row)

        return True

    def get_percentage_change(
        self, reference_price: float, current_price: float
    ) -> float:
        if current_price and reference_price:
            return round((current_price - reference_price) / reference_price * 100, 2)
        return None

    def get_by_date_range(
        self, df: pd.DataFrame, date_range: str, datetime_obj: datetime
    ) -> tuple[pd.Series, list[dict]]:
        from_date, to_date = DateRangeUtils().get_date_range_as_string(
            date_range=date_range,
            to_date=datetime_obj.date(),
            date_format="%Y-%m-%d",
            tz=VN_TIMEZONE,
        )

        if date_range == DateRangeUtils.DATE_RANGE_ALL:
            # Get the earliest record as reference price
            date_range_df = df[df["date"] >= from_date]
            if not date_range_df.empty:
                # Find the first price in the date range, mean the last available record
                ref_price = date_range_df.iloc[-1]
                chart_df = df[["date", "close"]][df["date"] >= from_date]
                chart_data = chart_df.sort_values(by=["date"], ascending=True).to_dict(
                    orient="records"
                )
                return ref_price, self.build_chart(chart_data)
        else:
            filtered_df = df[(df["date"] >= from_date) & (df["date"] <= to_date)]
            if not filtered_df.empty:
                # Find the first price in the date range, mean the last available record
                ref_price = filtered_df.iloc[-1]
                chart_df = filtered_df[["date", "close"]]
                chart_data = chart_df.sort_values(by=["date"], ascending=True).to_dict(
                    orient="records"
                )
                return ref_price, self.build_chart(chart_data)

        return pd.Series([], dtype="object"), []

    def build_chart(self, chart_data: list) -> list[dict]:
        chart_items = []
        for item in chart_data:
            if not self.is_nan(item["close"]) and not self.is_nan(item["date"]):
                avt = {
                    # "o": None,
                    # "h": None,
                    # "l": None,
                    "c": item["close"],
                    "t": (
                        item["date"]
                        if isinstance(item["date"], str)
                        else item["date"].timestamp()
                    ),
                    # "v": item['volume'],
                }
                chart_items.append(avt)
        return chart_items

    def indexing(self, items: list[dict]):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="ETFPriceChart", key_fields=["symbol"], payload=items
            )
            return success, response
        except Exception as ex:
            logger.error(f"Indexing chart error, {ex}.")
            return False, None

    def export_to_gcs(self, df: pd.DataFrame, input_date: str):
        gcs_path = f"marketdb/etf_price_chart/{input_date}/etf_price_chart.json"
        logger.info(f"Exporting data to {self.bucket_name}: {gcs_path}...")

        json_data = df.to_json(orient="records", lines=True)
        GCS().upload_dict(
            dict_json=json_data, bucket_name=self.bucket_name, gcs_path=gcs_path
        )

    def simplify_chart_data(self, chart, epsilon=0.01):
        """
        Simplifies the chart data using the RDP algorithm.
        epsilon: The tolerance for simplification 0.01 is ok for stock prices
        """
        if len(chart) <= 1000:
            return chart
        # Convert chart data to (t, c) pairs
        points = [(i, item["c"]) for i, item in enumerate(chart)]

        # Normalize the data
        t_vals = np.array([p[0] for p in points])
        c_vals = np.array([p[1] for p in points])

        t_range = t_vals.max() - t_vals.min() if t_vals.max() != t_vals.min() else 1
        c_range = c_vals.max() - c_vals.min() if c_vals.max() != c_vals.min() else 1

        normalized_points = [
            ((t - t_vals.min()) / t_range, (c - c_vals.min()) / c_range)
            for t, c in points
        ]

        # Apply RDP algorithm
        simplified_points = rdp_simplify(normalized_points, epsilon)

        # Convert back to original scale
        original_scale_points = [
            (int(t * t_range + t_vals.min()), c * c_range + c_vals.min())
            for t, c in simplified_points
        ]

        # Reconstruct chart format
        simplified_chart = []
        for idx, c in original_scale_points:
            if 0 <= idx < len(chart):
                simplified_chart.append(
                    {
                        "c": c,
                        "t": chart[idx]["t"],
                        # "original_idx": idx
                    }
                )

        return simplified_chart
