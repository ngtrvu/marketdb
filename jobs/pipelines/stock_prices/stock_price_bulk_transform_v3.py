import pandas as pd

from common.tinydwh.base import MiniJobBase
from utils.logger import logger as logging
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    get_date_str,
    str_to_datetime,
)
from common.mdb.client import MarketdbClient
from config import Config
from common.mdb.trading_calendar import TradingCalendar


class StockPriceBulkTransformV3(MiniJobBase, TradingCalendar):
    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    symbol: str
    exchange: str

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.new_lines = True
        self.marketdb_client = MarketdbClient()

        super().__init__()

    def pipeline(self, input_date: str = None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        # load the bulk stock prices on previous trading date
        input_date = self.get_previous_trading_date(input_date=input_date)
        logging.info(
            f"StockPriceBulkTransformV3: Loading bulk prices on {input_date}..."
        )

        self.data_frame = self._load_csv(
            input_date=input_date,
            exchange="HSX",
            base_path="crawler/cafef_stock_price_bulk",
        )

        if self.data_frame.empty:
            logging.error(
                f"StockPriceBulkTransformV3 Error: no data is loaded on {input_date}"
            )
            return False

        gcs_path = (
            f"marketdb/stock_price_ohlc_bulk_v3/{input_date}/stock_price_bulk.json"
        )
        self.export_to_gcs(
            df=self.data_frame, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
        )

        logging.info(f"Building stock price OHLC 250 days in VN100 on {input_date}...")
        self.upload_stock_price_ohlc_vn100(input_date=input_date)

        logging.info(
            f"StockPriceBulkTransformV3 on {input_date} is successfully executed."
        )
        return True

    def get_all_etf_symbols(self) -> list:
        symbols = self.marketdb_client.get_etf_symbols()
        symbols = list(set(symbols))
        symbols = sorted(symbols)

        return symbols


    def upload_stock_price_ohlc_vn100(self, input_date: str, n_year=4):
        vn100_symbols = []

        # load VN100 symbols from a file in gcs
        self.new_lines = False
        blobs = self.load_blobs(
            base_path="crawler/iboard_market_index_group",
            bucket_name=Config.BUCKET_NAME,
            input_date="2024/12/17",
            file_name_prefix="VN100.json",
        )
        for blob in blobs:
            json_str = self.ensure_json(blob.download_as_bytes().decode("utf-8"))
            if not json_str:
                logging.error(
                    f"Load vn100 symbols error: no data is loaded on {input_date}"
                )
                continue
            
            vn100_df = pd.read_json(json_str, lines=False)
            vn100_symbols = vn100_df["ss"].tolist()
            break

        # extract and upload the latest 250-day * n_year OHLC bulk prices in the list VN100
        d250_dates = (
            self.data_frame["date"]
            .drop_duplicates()
            .sort_values(ascending=False)[0 : 250 * n_year]
        )
        df = self.data_frame.query("symbol in @vn100_symbols and date in @d250_dates")
        logging.info(
            f"Uploading {len(df.index)} bulk prices OHLC 250 days in VN100 to GCS..."
        )
        self.export_to_gcs(
            df=df,
            bucket_name=Config.BUCKET_NAME,
            gcs_path=f"marketdb/stock_price_ohlc_250_days_vn100/{input_date}/stock_price_bulk.json",
        )

    def _load_csv(self, input_date: str, exchange: str, base_path: str = ""):
        date_obj = str_to_datetime(input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        cafef_date_dir = get_date_str(date_obj, date_format="%d.%m.%Y", tz=VN_TIMEZONE)

        gcs_path = f"gcs://{Config.BUCKET_NAME}/{base_path}/CafeF.{exchange}.Upto{cafef_date_dir}.csv"
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
