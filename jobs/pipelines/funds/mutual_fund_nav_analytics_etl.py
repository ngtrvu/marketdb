import time
import pandas as pd
from datetime import datetime
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.data import sub_dict
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
    get_datetime_now,
)
from utils.logger import logger
from common.tinydwh.storage.connector import GCS
from config import Config
from pipelines.funds.fund_performance import (
    compute_nav_change_rate,
    compute_nav_annualized_return,
    compute_maximum_drawdown,
)
from common.mdb.client import (
    MarketdbClient,
)


class MutualFundNAVAnalyticsETL(MiniJobBase):
    """
    This is mutual fund nav analytics the daily
    """

    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    analytics_rows: list = []
    chart_rows: list = []
    nav_inception_date = 10000.0
    bucket_name: str = ""

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.bucket_name = Config().get_bucket_name()
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.data_frame = self.load(
            input_date=input_date,
            bucket_name=self.bucket_name,
            base_path="marketdb/fund_nav_daily_bulk",
            file_name_prefix="fund_nav_daily",
        )

        is_transformed = self.transform()
        if not self.data_frame.empty and is_transformed:
            unique_symbols = self.data_frame["symbol"].unique().tolist()
            current_date = str_to_datetime(
                input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
            )
            for symbol in unique_symbols:
                analytics_row, chart_row = self.do_computing(
                    current_date=current_date, symbol=symbol
                )
                if analytics_row:
                    self.analytics_rows.append(analytics_row)
                if chart_row:
                    self.chart_rows.append(chart_row)

            # indexing analytics_items
            self.do_indexing(items=self.analytics_rows)
            self.do_indexing_v2(items=self.analytics_rows)

            self.upload_to_gcs(df=pd.DataFrame(self.analytics_rows))

            logger.info("MutualFundNAVAnalyticsETL is successfully executed")
            return True

        logger.warning("Warning: no data is loaded")
        return False

    def transform(self) -> bool:
        if self.data_frame.empty:
            return False
        self.data_frame = self.data_frame[["symbol", "date", "nav"]]
        self.data_frame["date"] = pd.to_datetime(
            self.data_frame["date"], format="%Y-%m-%d"
        )
        self.data_frame = self.data_frame.sort_values(
            by=["date", "symbol"], ascending=False
        )
        return True

    def __compute_annual_return(
        self,
        item: pd.Series,
        item_ny: pd.Series,
        default_item: pd.Series,
        n_year: int = 3,
    ) -> tuple[float, int]:
        if item.empty:
            return None, None

        if item_ny.empty and default_item.empty:
            return None, None

        annual_return = None
        initial_nav = item_ny.nav if not item_ny.empty else default_item.nav
        n_year = n_year if not item_ny.empty else 1

        change_rate = compute_nav_change_rate(
            present_value=item.nav, initial_value=initial_nav
        )
        annual_return = compute_nav_annualized_return(
            change_rate=change_rate, n_year=n_year
        )
        annual_return_percentage = annual_return * 100.0
        return annual_return_percentage, n_year

    def __compute_change_rate(self, current_item, initial_item):
        if current_item.empty or initial_item.empty:
            return None, None
        change_rate = compute_nav_change_rate(
            present_value=current_item.nav, initial_value=initial_item.nav
        )
        change_percentage = change_rate * 100 if change_rate is not None else None
        return change_rate, change_percentage

    def do_computing(self, current_date, symbol) -> dict:
        df = self.data_frame[self.data_frame["symbol"] == symbol]
        if df.empty:
            return None

        # get latest item
        item = df.iloc[0]

        # get items by time range
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

        # if we don't have enough data for n_year, we will compute annual return for 1 year
        annual_return_percentage, n_year = self.__compute_annual_return(
            item=item,
            item_ny=item_5y,
            default_item=item_1y,
            n_year=5,
        )
        change_rate_1w, change_percentage_1w = self.__compute_change_rate(
            current_item=item,
            initial_item=item_1w,
        )
        change_rate_1m, change_percentage_1m = self.__compute_change_rate(
            current_item=item,
            initial_item=item_1m,
        )
        change_rate_3m, change_percentage_3m = self.__compute_change_rate(
            current_item=item,
            initial_item=item_3m,
        )
        change_rate_6m, change_percentage_6m = self.__compute_change_rate(
            current_item=item,
            initial_item=item_6m,
        )
        change_rate_1y, change_percentage_1y = self.__compute_change_rate(
            current_item=item,
            initial_item=item_1y,
        )
        change_rate_3y, change_percentage_3y = self.__compute_change_rate(
            current_item=item,
            initial_item=item_3y,
        )
        change_rate_5y, change_percentage_5y = self.__compute_change_rate(
            current_item=item,
            initial_item=item_5y,
        )
        change_rate_ytd, change_percentage_ytd = self.__compute_change_rate(
            current_item=item,
            initial_item=item_ytd,
        )

        change_percentage_inception_date = compute_nav_change_rate(
            present_value=item.nav, initial_value=self.nav_inception_date
        )

        # MDD computation
        mdd = compute_maximum_drawdown(df["nav"])
        maximum_drawdown_percentage = mdd * 100.0 if mdd is not None else None

        # TODO: fix date, datetime - make sure it following the nav date
        analytics_row = {
            "symbol": symbol,
            "date": current_date.date(),
            "datetime": get_datetime_now(tz=VN_TIMEZONE),
            "nav": item.nav,
            "nav_1w": float(item_1w.nav) if not item_1w.empty else None,
            "nav_1m": float(item_1m.nav) if not item_1m.empty else None,
            "nav_3m": float(item_3m.nav) if not item_3m.empty else None,
            "nav_6m": float(item_6m.nav) if not item_6m.empty else None,
            "nav_1y": float(item_1y.nav) if not item_1y.empty else None,
            "nav_3y": float(item_3y.nav) if not item_3y.empty else None,
            "nav_5y": float(item_5y.nav) if not item_5y.empty else None,
            "nav_ytd": float(item_ytd.nav) if not item_ytd.empty else None,
            "nav_inception_date": self.nav_inception_date,
            "change_percentage_1w": change_percentage_1w,
            "change_percentage_1m": change_percentage_1m,
            "change_percentage_3m": change_percentage_3m,
            "change_percentage_6m": change_percentage_6m,
            "change_percentage_1y": change_percentage_1y,
            "change_percentage_3y": change_percentage_3y,
            "change_percentage_5y": change_percentage_5y,
            "change_percentage_ytd": change_percentage_ytd,
            "change_percentage_inception_date": change_percentage_inception_date,
            "annualized_return_percentage": annual_return_percentage,
            "annualized_return_n_year": n_year,
            "maximum_drawdown_percentage": maximum_drawdown_percentage,
        }

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
            "movement_ytd": chart_ytd,
        }

        return analytics_row, chart_row

    def get_by_date_range(
        self, df: pd.DataFrame, date_range: str, datetime_obj: datetime
    ) -> tuple[pd.Series, list]:
        from_date, to_date = DateRangeUtils().get_date_range_as_string(
            date_range=date_range,
            to_date=datetime_obj.date(),
            date_format="%Y-%m-%d",
            tz=VN_TIMEZONE,
        )

        date_range_df = df[df["date"] <= from_date]
        chart_df = df[["date", "nav"]][df["date"] >= from_date]
        chart_data = chart_df.sort_values(by=["date"], ascending=True).to_dict(
            orient="records"
        )
        if not date_range_df.empty:
            return date_range_df.iloc[0], self.__build_chart(chart_data or [])
        return pd.Series([], dtype="object"), []

    def __build_chart(self, chart_data: list) -> list[dict]:
        chart_items = []
        for item in chart_data:
            avt = {
                "o": None,
                "h": None,
                "l": None,
                "c": item["nav"],
                "t": time.mktime(item["date"].timetuple()),
            }
            chart_items.append(avt)
        return chart_items

    def do_indexing(self, items: list):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="FundNavAnalytics",
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

    def do_indexing_v2(self, items: list):
        selected_items = []
        selected_fields = [
            "symbol",
            "nav",
            "nav_1w",
            "nav_1m",
            "nav_3m",
            "nav_6m",
            "nav_1y",
            "nav_3y",
            "nav_5y",
            "nav_ytd",
            "nav_inception_date",
            "change_percentage_1w",
            "change_percentage_1m",
            "change_percentage_3m",
            "change_percentage_6m",
            "change_percentage_1y",
            "change_percentage_3y",
            "change_percentage_5y",
            "change_percentage_ytd",
            "change_percentage_inception_date",
            "annualized_return_percentage",
            "annualized_return_n_year",
            "maximum_drawdown_percentage",
        ]
        for item in items:
            selected_items.append(
                sub_dict(
                    keys=selected_fields,
                    dict_obj=item,
                )
            )

        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="MutualFundNavIndex",
                key_fields=["symbol"],
                payload=selected_items,
            )

            if not success:
                logger.error(f"Error indexing: {response}")
                return False

            logger.debug(f"Indexing response: {response}")
            return True

        except Exception as ex:
            logger.error(f"Error indexing: {ex}")
            return False

    def upload_to_gcs(
        self,
        df=pd.DataFrame(),
        namespace="marketdb",
        dataset_name: str = "fund_nav_analytics",
        date_str: str = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE),
        file_name: str = "fund_nav_analytics.json",
    ):
        gcs_path = f"{namespace}/{dataset_name}/{date_str}/{file_name}"
        json_data = df.to_json(orient="records", lines=True)

        gcs = GCS()
        gcs.upload_dict(
            dict_json=json_data,
            bucket_name=self.bucket_name,
            gcs_path=gcs_path,
        )

        logger.info(f"Uploaded data to GCS: gs://{self.bucket_name}/{gcs_path} ...")
