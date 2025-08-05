import pandas as pd
import numpy as np

from utils.logger import logger
from common.tinydwh.base import MiniJobBase
from common.tinydwh.date_ranges import DateRangeUtils
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    get_datetime_now,
    str_to_datetime,
)
from common.tinydwh.storage.connector import GCS
from common.mdb.client import MarketdbClient
from config import Config


class MutualFundNavPriceChart(MiniJobBase):
    """
    This is the pipeline for mutual fund nav price chart
    """

    def __init__(self, sampling_ratio=1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.marketdb_client = MarketdbClient()

        super().__init__()

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        input_date_obj = str_to_datetime(input_date, "%Y/%m/%d", tz=None)

        # load mutual fund daily NAVs from GCS
        fund_nav_daily_df = self.load(
            bucket_name=Config.BUCKET_NAME, base_path="marketdb/fund_nav_daily_bulk"
        )

        if fund_nav_daily_df.empty:
            logger.error("Mutual fund NAV Daily Bulk data is empty...")
            return False

        fund_nav_daily_df = fund_nav_daily_df[["symbol", "date", "nav"]]
        daily_nav_groups = fund_nav_daily_df.sort_values(
            by=["date"], ascending=False
        ).groupby(["symbol"], as_index=False)

        # get the latest daily nav row of each group
        latest_nav_each_group_df = daily_nav_groups.first()
        now_date_time = get_datetime_now(tz=VN_TIMEZONE)
        fund_nav_price_chart_df = pd.DataFrame()

        for _, latest_nav in latest_nav_each_group_df.iterrows():
            df = daily_nav_groups.get_group(latest_nav["symbol"])

            # get the NAV row whose date is closest to input_date and must be less than or equal to input_date
            closest_nav = latest_nav
            if input_date_obj < latest_nav["date"]:
                closest_nav = df[df["date"] <= input_date].iloc[0]

            closest_input_date = closest_nav["date"]
            # change format of datetime and convert datetime to string
            closest_input_date = str(closest_input_date.strftime("%Y/%m/%d"))

            change_value_1w, change_percentage_1w, nav_1w = self.compute(
                df=df,
                closest_nav=closest_nav,
                date_range=DateRangeUtils.DATE_RANGE_1W,
                input_date=closest_input_date,
            )
            change_value_1m, change_percentage_1m, nav_1m = self.compute(
                df=df,
                closest_nav=closest_nav,
                date_range=DateRangeUtils.DATE_RANGE_1M,
                input_date=closest_input_date,
            )
            change_value_3m, change_percentage_3m, nav_3m = self.compute(
                df=df,
                closest_nav=closest_nav,
                date_range=DateRangeUtils.DATE_RANGE_3M,
                input_date=closest_input_date,
            )
            change_value_6m, change_percentage_6m, nav_6m = self.compute(
                df=df,
                closest_nav=closest_nav,
                date_range=DateRangeUtils.DATE_RANGE_6M,
                input_date=closest_input_date,
            )
            change_value_1y, change_percentage_1y, nav_1y = self.compute(
                df=df,
                closest_nav=closest_nav,
                date_range=DateRangeUtils.DATE_RANGE_1Y,
                input_date=closest_input_date,
            )
            change_value_3y, change_percentage_3y, nav_3y = self.compute(
                df=df,
                closest_nav=closest_nav,
                date_range=DateRangeUtils.DATE_RANGE_3Y,
                input_date=closest_input_date,
            )
            change_value_5y, change_percentage_5y, nav_5y = self.compute(
                df=df,
                closest_nav=closest_nav,
                date_range=DateRangeUtils.DATE_RANGE_5Y,
                input_date=closest_input_date,
            )
            change_value_ytd, change_percentage_ytd, nav_ytd = self.compute(
                df=df,
                closest_nav=closest_nav,
                date_range=DateRangeUtils.DATE_RANGE_YTD,
                input_date=closest_input_date,
            )

            nav_row = {
                "symbol": closest_nav["symbol"],
                "date": closest_nav["date"],
                "datetime": closest_input_date,
                "nav_1w": nav_1w,
                "nav_1m": nav_1m,
                "nav_3m": nav_3m,
                "nav_6m": nav_6m,
                "nav_1y": nav_1y,
                "nav_3y": nav_3y,
                "nav_5y": nav_5y,
                "nav_ytd": nav_ytd,
                "change_value_1w": change_value_1w,
                "change_percentage_1w": change_percentage_1w,
                "change_value_1m": change_value_1m,
                "change_percentage_1m": change_percentage_1m,
                "change_value_3m": change_value_3m,
                "change_percentage_3m": change_percentage_3m,
                "change_value_6m": change_value_6m,
                "change_percentage_6m": change_percentage_6m,
                "change_value_1y": change_value_1y,
                "change_percentage_1y": change_percentage_1y,
                "change_value_3y": change_value_3y,
                "change_percentage_3y": change_percentage_3y,
                "change_value_5y": change_value_5y,
                "change_percentage_5y": change_percentage_5y,
                "change_value_ytd": change_value_ytd,
                "change_percentage_ytd": change_percentage_ytd,
            }
            fund_nav_price_chart_df = pd.concat(
                [fund_nav_price_chart_df, pd.DataFrame(nav_row, index=["symbol"])]
            )

        # ensure date is in dd-mm-yyyy format by converting to datetime and then to date by pandas
        fund_nav_price_chart_df["date"] = pd.to_datetime(
            fund_nav_price_chart_df["date"]
        ).dt.date

        fund_nav_price_chart_df = fund_nav_price_chart_df.replace({np.nan: None})

        # upload to gcs
        self.upload_to_gcs(df=fund_nav_price_chart_df)

        # index to db, convert to dict and then to list
        items = fund_nav_price_chart_df.to_dict("records")

        # convert date to dd-mm-yyyy format
        for item in items:
            item["date"] = item["date"].strftime("%d-%m-%Y")

        self.do_indexing(items)

        logger.info("MutualFundNavPriceChart is successfully executed!")
        return True

    def compute(
        self, df: pd.DataFrame, closest_nav: pd.Series, date_range: str, input_date: str
    ) -> tuple[float, float, float]:
        row = self.get_row_by_date_range(
            df=df, date_range=date_range, input_date=input_date
        )

        if row is not None and not row.empty:
            value_change = closest_nav["nav"] - row["nav"]
            return value_change, (value_change * 100) / row["nav"], row["nav"]
        return None, None, None

    def get_row_by_date_range(self, df: pd.DataFrame, date_range: str, input_date: str):
        datetime_obj = str_to_datetime(
            input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )
        from_date, _ = DateRangeUtils().get_date_range_as_string(
            date_range=date_range,
            to_date=datetime_obj.date(),
            date_format="%Y-%m-%d",
            tz=VN_TIMEZONE,
        )

        date_range_df = df[df["date"] <= from_date]

        if not date_range_df.empty:
            return date_range_df.iloc[0]
        return None

    def do_indexing(self, items: list):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="MutualFundPriceChart",
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

    def upload_to_gcs(
        self,
        df=pd.DataFrame(),
        namespace="marketdb",
        dataset_name: str = "fund_nav_price_chart",
        date_str: str = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE),
        file_name: str = "fund_nav_price.json",
    ):
        gcs_path = f"{namespace}/{dataset_name}/{date_str}/{file_name}"
        json_data = df.to_json(orient="records", lines=True)

        gcs = GCS()
        gcs.upload_dict(
            dict_json=json_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
        )

        logger.info(
            f"Uploaded fund NAV prices with size {df.shape} to GCS: {gcs_path} ..."
        )
