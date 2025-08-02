import random
import time

from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str
from utils.logger import logger as logging
from common.tinydwh.base import MiniJobBase

from pipelines.crawlers.crawler_mutual_funds_nav.main import (
    mutual_funds_nav_history_main,
)
from config import Config
from pipelines.crawlers.crawler_mutual_funds_nav.config import (
    ALL_SYMBOLS,
    SYMBOLS_BY_SOURCE,
    MutualFundSource,
)


class MutualFundNAVBackfill(MiniJobBase):
    """
    This is backfilling the mutual fund NAV
    """

    def __init__(self):
        super().__init__()
        self.bucket_name = Config().get_bucket_name()

    def pipeline(
        self,
        input_date: str = None,
        symbol: str = None,
        fund_manager: int = None,
        start_date: str = None,
        end_date: str = None,
    ):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        result = {}
        base_path = "crawler/mutual_fund_nav_history"
        symbols = []

        if symbol:
            symbols = [symbol]
        elif fund_manager and MutualFundSource(fund_manager):
            symbols = SYMBOLS_BY_SOURCE[MutualFundSource(fund_manager)]
        else:
            symbols = ALL_SYMBOLS

        logging.info(f"Backfilling symbols: {symbols}")
        for symbol in symbols:
            try:
                data = mutual_funds_nav_history_main(
                    symbol=symbol,
                    base_path=base_path,
                    bucket_name=self.bucket_name,
                    start_date=start_date,
                    end_date=end_date,
                )
                result[symbol] = data

                # sleep for a random number of seconds to avoid being blocked by the server
                seconds = random.randint(1, 5)
                logging.info(f"Sleeping for {seconds} seconds...")
                time.sleep(seconds)
            except Exception as e:
                logging.error(f"Failed to backfill {symbol} caused by {e}")
                continue

        return result

    def run_etl(
        self,
        input_date: str = None,
        symbol: str = None,
        from_date: str = None,
        to_date: str = None,
    ):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        base_path = f"crawler/mutual_fund_nav_history/{input_date}"
        bucket_name = Config.BUCKET_NAME

        # example: DCBF_nav_history_upto_20250624.json
        if symbol:
            date_str = input_date.replace("/", "")
            file_name = f"{symbol}_nav_history_upto_{date_str}.json"
        else:
            file_name = None

        logging.info(f"Loading data from {bucket_name}/{base_path}/{file_name}")
        self.new_lines = False
        df = self.load(
            bucket_name=bucket_name, base_path=base_path, file_name_prefix=file_name
        )
        if df.empty:
            raise Exception(f"Mutual fund NAV history data is empty for {input_date}")

        if from_date:
            df = df[df["date"] >= from_date]
        if to_date:
            df = df[df["date"] <= to_date]

        # for each day, we export the data to a new file
        for nav_date, nav_df in df.groupby("date"):
            # format date as YYYY/MM/DD for building path
            date_str = nav_date.strftime("%Y/%m/%d")

            # create a file name: fund_nav_DCDS.json
            file_name = f"fund_nav_{symbol}.json"

            gcs_path = f"crawler/mutual_fund_daily_nav/{date_str}/{file_name}"
            logging.debug(f"Exporting {bucket_name}/{gcs_path} to GCS...")
            self.export_to_gcs(df=nav_df, bucket_name=bucket_name, gcs_path=gcs_path)
