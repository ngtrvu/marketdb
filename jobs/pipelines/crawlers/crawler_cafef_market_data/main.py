import logging
import os
import uuid
import zipfile
from time import sleep

import wget

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
)
from common.tinydwh.storage.connector import GCS
from common.mdb.trading_calendar import TradingCalendar

CAFEF_CDN = "https://cafef1.mediacdn.vn/data/ami_data"


class CafeFMarketDataCrawler(MiniJobBase, TradingCalendar):

    def __init__(self):
        self.bucket_name = os.environ.get("BUCKET_NAME", "stock_analytics")
        self.namespace = "crawler"

        super().__init__()

    def pipeline(self, input_date: str = "", adjusted: bool = True):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(input_date):
            logging.info(f"CafeFMarketDataCrawler: No trading today: {input_date}")

        download_input_date = self.get_previous_trading_date(input_date)
        self.download_stock_price_bulk(download_input_date)

        sleep(1)

        self.download_stock_price_eod(download_input_date, adjusted)

        sleep(1)

        self.download_market_index_bulk(download_input_date)

        logging.info("StockPriceDailyCafef has been completed")
        return True

    def download_stock_price_bulk(self, input_date: str):
        # Download all EOD historical data
        dataset_name = "cafef_stock_price_bulk"
        logging.info(f"Downloading full stock price data up to {input_date}")
        gcs_path = f"{self.namespace}/{dataset_name}"

        # i.e. "https://cafef1.mediacdn.vn/data/ami_data/20221122/CafeF.SolieuGD.Upto22112022.zip"
        cafef_file_path = self.get_cafef_data_path(input_date, "SolieuGD", is_bulk=True)
        success = self.download_to_gcs(
            url=cafef_file_path,
            bucket_name=self.bucket_name,
            base_path=gcs_path,
        )

        if not success:
            logging.warning(
                "StockPriceDailyCafef().pipeline() full historical data with_adjusted failed"
            )
            return False
        return True

    def download_stock_price_eod(self, input_date: str, adjusted: bool = True):
        # Download today EOD historical data
        dataset_name = "cafef_stock_price_daily"
        logging.info(f"Downloading EOD {input_date}")
        gcs_path = f"{self.namespace}/{dataset_name}/{input_date}"

        if adjusted:
            cafef_file_path = self.get_cafef_data_path(
                input_date, "SolieuGD", is_bulk=False
            )
        else:
            cafef_file_path = self.get_cafef_data_path(
                input_date, "SolieuGD.Raw", is_bulk=False
            )

        success = self.download_to_gcs(
            url=cafef_file_path,
            bucket_name=self.bucket_name,
            base_path=gcs_path,
        )

        if not success:
            logging.warning(
                "StockPriceDailyCafef().pipeline() EOD data with_adjusted failed"
            )
            return False
        return True

    def download_market_index_bulk(self, input_date: str = ""):
        # Download market index historical data up to date
        dataset_name = "cafef_market_index_bulk"

        logging.info(f"Downloading full market index data up to {input_date}")
        gcs_path = f"{self.namespace}/{dataset_name}"

        # i.e. "https://cafef1.mediacdn.vn/data/ami_data/20221122/CafeF.Index.Upto22112022.zip"
        cafef_file_path = self.get_cafef_data_path(input_date, "Index", is_bulk=True)
        success = self.download_to_gcs(
            url=cafef_file_path,
            bucket_name=self.bucket_name,
            base_path=gcs_path,
        )

        if not success:
            logging.warning(
                "StockPriceDailyCafef().pipeline() full market index data failed"
            )
            return False

    def download_to_gcs(self, url: str, bucket_name: str, base_path: str) -> bool:
        try:
            filename = os.path.basename(url)
            file_path = f"tmp/{filename}"
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as ex:
            logging.warning(f"Remove existing file failed, error: {ex}")

        downloaded = False
        attempts = 0
        while not downloaded and attempts < 3:
            try:
                filename = wget.download(url)
                logging.debug(f"Downloaded to gcs: {filename}")
                downloaded = True
            except Exception as ex:
                logging.info(f"Download from {url} error, {ex}")
                attempts += 1
                sleep(1)

        if not downloaded:
            logging.error(f"Download from {url} error")
            return False

        try:
            # unzip file
            unzip_dir = f"tmp/{str(uuid.uuid4())}"
            with zipfile.ZipFile(filename, "r") as zip_ref:
                zip_ref.extractall(unzip_dir)
        except Exception as ex:
            logging.warning(f"Unzip {url} error: {ex}")
            return False

        for file in os.listdir(unzip_dir):
            gcs_path = f"{base_path}/{file}"
            logging.debug(f"Upload to gcs {filename}: {gcs_path}")

            gcs = GCS()
            gcs.upload_file(
                local_path=f"{unzip_dir}/{file}",
                bucket_name=self.bucket_name,
                gcs_path=gcs_path,
            )

        return True

    def get_cafef_data_path(
        self, input_date: str, data_type: str, is_bulk: bool = True
    ):
        """
        Get cafef data path

        Args:
            input_date: str
            data_type: str (e.g. "SolieuGD", "Index")
            is_bulk: bool
        """
        date_obj = str_to_datetime(input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        cafef_date_dir = get_date_str(date_obj, date_format="%Y%m%d", tz=VN_TIMEZONE)
        cafef_date_str = get_date_str(date_obj, date_format="%d%m%Y", tz=VN_TIMEZONE)
        bulk_prefix = "Upto" if is_bulk else ""

        return f"{CAFEF_CDN}/{cafef_date_dir}/CafeF.{data_type}.{bulk_prefix}{cafef_date_str}.zip"
