import pandas as pd

from utils.logger import logger as logging
from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str, str_to_datetime
from common.mdb.client import MarketdbClient
from config import Config


class StockPriceBulkTransform(MiniJobBase):
    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    symbol: str
    exchange: str

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True

        super().__init__()

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        datetime_obj = str_to_datetime(input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        is_trading_date = MarketdbClient().check_calendar(datetime_obj=datetime_obj)
        if not is_trading_date:
            logging.info(f"StockPriceBulkTransform: No trading today: {input_date}")
            return True

        exchanges = {
            "hose": "HSX",
            "hnx": "HNX",
            "upcom": "UPCOM",
        }

        for key, val in exchanges.items():
            self.data_frame = self._load_csv(
                input_date=input_date, exchange=val, base_path=f"crawler/cafef_stock_price_bulk"
            )

            if self.data_frame.empty:
                logging.error(f"StockPriceBulkTransform Error: no data is loaded for {key}")
            else:
                gcs_path = f"marketdb/stock_price_ohlc_bulk/{input_date}/{key}.json"
                self.export_to_gcs(
                    df=self.data_frame, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
                )
                logging.info(f"StockPriceBulkTransform for {key} is successfully executed.")
        return True

    def _load_csv(self, input_date: str, exchange: str, base_path: str = ""):
        date_obj = str_to_datetime(input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        cafef_date_dir = get_date_str(date_obj, date_format="%d.%m.%Y", tz=VN_TIMEZONE)

        gcs_path = (
            f"gcs://{Config.BUCKET_NAME}/{base_path}/CafeF.{exchange}.Upto{cafef_date_dir}.csv"
        )
        logging.info(f"Loading csv data from {gcs_path}")

        try:
            df = pd.read_csv(gcs_path)
        except Exception as ex:
            logging.error(ex)
            return pd.DataFrame()

        df = df.rename(
            columns={
                "<Ticker>": "symbol",
                "<DTYYYYMMDD>": "date",
                "<Open>": "open",
                "<High>": "high",
                "<Low>": "low",
                "<Close>": "close",
                "<Volume>": "volume",
            }
        )
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.date
        df["open"] = df["open"] * 1000
        df["high"] = df["high"] * 1000
        df["low"] = df["low"] * 1000
        df["close"] = df["close"] * 1000
        return df
