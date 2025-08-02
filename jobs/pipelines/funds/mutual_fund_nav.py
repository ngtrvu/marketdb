import random
import time
import pandas as pd

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str
from utils.logger import logger
from common.mdb.client import MarketdbClient
from config import Config
from pipelines.crawlers.crawler_mutual_funds_nav.main import (
    mutual_funds_nav_daily_main,
)
from pipelines.crawlers.crawler_mutual_funds_nav.config import (
    ALL_SYMBOLS,
    SYMBOLS_BY_SOURCE,
    MutualFundSource,
)


class MutualFundNAVCrawler(MiniJobBase):
    """
    This is crawling the intraday NAV of mutual funds
    """

    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    bucket_name: str = ""

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = False
        self.bucket_name = Config().get_bucket_name()
        self.marketdb_client = MarketdbClient()

        super().__init__()

    def pipeline(
        self, input_date: str = None, fund_manager: int = None, symbol: str = None
    ):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        result = {}
        base_path = "crawler/mutual_fund_daily_nav"
        symbols = []

        if fund_manager and MutualFundSource(fund_manager):
            # convert fund_manager to enum
            symbols = SYMBOLS_BY_SOURCE[MutualFundSource(fund_manager)]
        else:
            symbols = [symbol] if symbol else ALL_SYMBOLS

        logger.info(f"Crawling symbols: {symbols}")
        for symbol in symbols:
            try:
                data = mutual_funds_nav_daily_main(
                    symbol=symbol,
                    base_path=base_path,
                    bucket_name=self.bucket_name,
                    gcs_date=input_date,
                )
                result[symbol] = data

                # sleep for a random number of seconds to avoid being blocked by the server
                seconds = random.randint(1, 10)
                logger.info(f"Sleeping for {seconds} seconds...")
                time.sleep(seconds)
            except Exception as e:
                logger.error(f"Failed to crawl {symbol} caused by {e}")
                continue

        if len(result) == 0:
            logger.warning("Error: no data is loaded")
            return False

        logger.info("MutualFundNAVDailyETL is successfully executed.")
        return True
