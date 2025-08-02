from datetime import timedelta

import numpy as np
import pandas as pd

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    date_str_reformat,
    get_date_str,
    str_to_datetime,
)
from utils.logger import logger
from common.tinydwh.storage.connector import GCS
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class StockPriceHistoryInit(MiniJobBase):
    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    selected_fields = [
        # must have data
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "exchange",
        # # intraday data
        # "type",
        # "timestamp",
        # "reference",
        # "ceiling",
        # "floor",
        # "price",
        # "trading_value",
    ]

    adjusted_fields = [
        # "reference",
        # "ceiling",
        # "floor",
        "open",
        "high",
        "low",
        "close",
        # "price",
    ]

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio

        super().__init__()

    def pipeline(self, input_date: str = None) -> bool:
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            logger.info(f"StockPriceHistoryInit: No trading today {input_date}...")
            return True

        # load daily stock prices on input_date
        daily_prices_df = self.load_daily_stock_prices(date_str=input_date)
        if daily_prices_df.empty:
            logger.info(
                f"StockPriceHistoryInit: No daily trading data is loaded on {input_date}..."
            )
            return False

        # load the bulk stock prices on previous trading date
        max_attempts = 5
        attempt_count = 0
        bulk_prices_df: pd.DataFrame = pd.DataFrame()
        previous_trading_date = input_date
        while attempt_count < max_attempts:
            attempt_count += 1
            previous_trading_date = self.get_previous_trading_date_str(
                date_str=previous_trading_date
            )
            logger.info(
                f"StockPriceHistoryInit: Loading bulk prices on {previous_trading_date}..."
            )
            bulk_prices_df = self.load_bulk_stock_prices(date_str=previous_trading_date)
            if bulk_prices_df.empty:
                logger.warning(
                    f"StockPriceHistoryInit Warning: No bulk prices OHLC on {previous_trading_date}"
                )
                continue

            logger.info(
                f"Loaded historical bulk prices {bulk_prices_df.shape} on {previous_trading_date}."
            )
            break

        if bulk_prices_df.empty:
            logger.error(
                f"StockPriceHistoryInit Error: No bulk prices OHLC is loaded after {max_attempts} attempts."
            )
            return False

        # load the stock corporate actions on input_date
        stock_corporate_actions_df = self.load_stock_corporate_actions_daily(
            date_str=input_date
        )
        if stock_corporate_actions_df.empty:
            logger.info(
                f"StockPriceHistoryInit: No stock corporate actions on {input_date}..."
            )
            self.data_frame = pd.concat(
                [daily_prices_df, bulk_prices_df], ignore_index=True
            )
        else:
            logger.info(
                f"Loaded stock corporate actions {stock_corporate_actions_df.shape}."
            )
            bulk_adjusted_prices_df = self.adjust_ohlc_prices(
                bulk_prices_df=bulk_prices_df,
                stock_corporate_actions_df=stock_corporate_actions_df,
                date_str=input_date,
            )
            self.data_frame = pd.concat(
                [daily_prices_df, bulk_adjusted_prices_df], ignore_index=True
            )

        if self.data_frame.empty:
            logger.error(
                f"StockPriceHistoryInit Error: No trading data to export to GCS on {input_date}..."
            )
            return False

        # convert 'date' field from timestamps to strings of date
        # self.data_frame = self.convert_timestamps_to_date_strs(self.data_frame)
        self.data_frame["date"] = self.data_frame["date"].apply(
            lambda x: self.ensure_date_str(x)
        )

        self.upload_data_frame_to_gcs(
            dataset_name="stock_price_ohlc_bulk_v3",
            date_str=input_date,
            file_name="stock_price_bulk.json",
        )

        logger.info(
            f"StockPriceHistoryInit on {input_date} is successfully executed..."
        )
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

    def get_ex_dividend_price(
        self,
        price,
        stock_issuance_ratio,
        stock_dividend_ratio,
        cash_value,
        par_value=10_000,
    ):
        return (price + par_value * stock_issuance_ratio - cash_value) / (
            1 + stock_issuance_ratio + stock_dividend_ratio
        )

    def convert_timestamps_to_date_strs(self, df: pd.DataFrame) -> pd.DataFrame:
        # convert integer timestamp to datetime
        df["date"] = pd.to_datetime(df["timestamp"], unit="s")
        # convert UTC to Vietnam timezone
        df["date"] = df["date"].dt.tz_localize("UTC").dt.tz_convert(VN_TIMEZONE)
        # format datetime as date string
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        return df

    def load_daily_stock_prices(self, date_str: str):
        self.new_lines = True
        df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_price_intraday",
            input_date=date_str,
            file_name_prefix="stock_price_ohlc.json",
        )
        if not df.empty:
            logger.info(f"Load daily trading data on {date_str} successfully...")
            if "date" not in df.columns:
                df = self.convert_timestamps_to_date_strs(df)
            for col in self.selected_fields:
                if col not in df.columns:
                    df[col] = None

            return df[self.selected_fields]

        return pd.DataFrame()

    def load_bulk_stock_prices(self, date_str: str):
        self.new_lines = True
        df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_price_ohlc_bulk_v3",
            input_date=date_str,
            file_name_prefix="stock_price_bulk.json",
        )
        if not df.empty:
            logger.info(f"Loaded bulk stock prices on {date_str} successfully...")
            if "date" not in df.columns:
                df = self.convert_timestamps_to_date_strs(df)
            return df[self.selected_fields]

        return pd.DataFrame()

    def ensure_date_str(self, input: any) -> str:
        if isinstance(input, str):
            return input
        if isinstance(input, pd.Timestamp):
            return input.strftime("%Y-%m-%d")
        return input

    def load_stock_corporate_actions_daily(self, date_str: str):
        self.new_lines = True
        selected_fields = [
            "symbol",
            "exrightDate",
            "issueDate",
            "eventType",
            "value",
            "ratio",
        ]
        stock_corporate_actions_df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/corporate_action",
            input_date=date_str,
            file_name_prefix="corporate_action.json",
        )
        if not stock_corporate_actions_df.empty:
            return stock_corporate_actions_df[selected_fields]

        return pd.DataFrame()

    def is_last_trading_date_price(self, ohlc_price: tuple) -> bool:
        is_last_price = True
        for price in ohlc_price:
            if price <= 0:
                is_last_price = False
                break
        return is_last_price

    def adjust_ohlc_prices(
        self,
        bulk_prices_df: pd.DataFrame,
        stock_corporate_actions_df: pd.DataFrame,
        date_str: str,
    ):
        # get all stock events on input_date with 'stock' or 'cash' in eventType
        event_types = ["CASHDIVIDEND", "STOCKDIVIDEND", "STOCKISSUANCE"]
        input_date_reformatted = date_str_reformat(
            date_str, date_format="%Y/%m/%d", to_date_format="%Y-%m-%d"
        )
        stock_event_by_date_df = stock_corporate_actions_df.query(
            "eventType.str.upper() in @event_types &"
            "exrightDate == @input_date_reformatted"
        )
        stock_event_grouped_df = stock_event_by_date_df.groupby(["symbol"])

        # adjust bulk OHLC stock prices of dividend symbols (in the previous trading dates)
        for symbol in stock_event_grouped_df.groups:
            stock_issuance_ratio = 0
            stock_dividend_ratio = 0
            cash_value = 0

            event_df = stock_event_grouped_df.get_group(symbol)
            event_stock_dividend_df = event_df.query(
                "eventType.str.upper() == 'STOCKDIVIDEND'"
            )
            event_stock_issuance_df = event_df.query(
                "eventType.str.upper() == 'STOCKISSUANCE'"
            )
            event_cash_df = event_df.query("eventType.str.upper() == 'CASHDIVIDEND'")

            if not event_stock_dividend_df.empty:
                event_stock_dividend_df.reset_index(drop=True, inplace=True)
                stock_dividend_ratio = event_stock_dividend_df["ratio"].sum()

            if not event_stock_issuance_df.empty:
                event_stock_issuance_df.reset_index(drop=True, inplace=True)
                stock_issuance_ratio = event_stock_issuance_df["ratio"].sum()

            if not event_cash_df.empty:
                event_cash_df.reset_index(drop=True, inplace=True)
                cash_value = event_cash_df["value"].sum()

            # filter out prices of the dividend symbol
            mask = bulk_prices_df["symbol"] == symbol
            bulk_prices_event_df = bulk_prices_df[mask]

            if bulk_prices_event_df.empty:
                continue

            previous_trading_date_str = self.get_previous_trading_date_str(
                date_str=date_str
            )
            last_trading_date_price_ds = bulk_prices_event_df.query(
                "date == @previous_trading_date_str"
            )
            if last_trading_date_price_ds.empty:
                continue
            last_trading_date_price_ds.reset_index(drop=True, inplace=True)

            for col in self.adjusted_fields:
                # get the ex-dividend ratio between adjusted price and raw price
                price_yesterday_raw = last_trading_date_price_ds.loc[0, col]
                price_yesterday_adjusted = self.get_ex_dividend_price(
                    price=price_yesterday_raw,
                    stock_issuance_ratio=stock_issuance_ratio,
                    stock_dividend_ratio=stock_dividend_ratio,
                    cash_value=cash_value,
                )
                ex_dividend_ratio = price_yesterday_adjusted / price_yesterday_raw

                # multiply ex-dividend ratio by the raw prices
                bulk_prices_df.loc[mask, col] *= ex_dividend_ratio
                bulk_prices_df.loc[mask, col] = round(bulk_prices_df.loc[mask, col])

        return bulk_prices_df

    def upload_data_frame_to_gcs(
        self,
        namespace="marketdb",
        dataset_name: str = "stock_price_ohlc_bulk_v3",
        date_str: str = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE),
        file_name: str = "stock_price_bulk.json",
    ):
        gcs_path = f"{namespace}/{dataset_name}/{date_str}/{file_name}"
        json_data = self.data_frame.to_json(orient="records", lines=True)

        gcs = GCS()
        gcs.upload_dict(
            dict_json=json_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path
        )

        logger.info(
            f"Uploaded bulk prices OHLC with size {self.data_frame.shape} to GCS: {gcs_path} ..."
        )
