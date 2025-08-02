import os
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
from utils.logger import logger, setup_logger
from common.fear_greed_index.constants import VN100
from common.tinydwh.storage.connector import GCS
from common.mdb.client import MarketdbClient
from config import Config

setup_logger(level=os.environ.get("LOG_LEVEL", "INFO"))


class StockPriceHistoryReset(MiniJobBase):
    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio

    def pipeline(self, input_date: str = None) -> bool:
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        if not self.is_trading_date(date_str=input_date):
            return False

        logger.info(f"Merge Stag bulk prices V2 and VNDirect bulk prices on {input_date}...")
        self.data_frame = self.merge_historical_bulk_prices(input_date=input_date)
        if not self.data_frame.empty:
            self.upload_data_frame_to_gcs(
                dataset_name="stock_price_ohlc_bulk_v2",
                date_str=input_date,
                file_name="stock_price_bulk.json",
            )
            return True

        logger.info(f"StockPriceHistoryReset on {input_date} is successfully executed...")
        return True

    def is_trading_date(self, date_str: str) -> bool:
        datetime_obj = str_to_datetime(input_str=date_str, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        return MarketdbClient().check_calendar(datetime_obj=datetime_obj)

    def get_yesterday_str(self, input_date: str) -> str:
        datetime_obj = str_to_datetime(input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        return get_date_str(
            datetime_obj - timedelta(days=1), date_format="%Y/%m/%d", tz=VN_TIMEZONE
        )

    def get_previous_trading_date_str(self, date_str: str) -> str:
        """Get the most recent previous trading date."""
        most_recent_trading_date = self.get_yesterday_str(input_date=date_str)

        while not self.is_trading_date(date_str=most_recent_trading_date):
            most_recent_trading_date = self.get_yesterday_str(input_date=most_recent_trading_date)

        return most_recent_trading_date

    def normalize_iboard_symbol_prices(self, ohlc_prices: pd.DataFrame) -> pd.DataFrame:
        ohlc_prices = ohlc_prices.drop_duplicates(subset=["date"])

        mask = ohlc_prices["volume"].isnull()
        ohlc_prices.loc[mask, "volume"] = 0

        mask = ohlc_prices["volume"] == 0
        ohlc_prices.loc[mask, ["open", "high", "low"]] = np.nan
        ohlc_prices.loc[mask, ["close"]] = ohlc_prices.loc[mask, "reference"]

        # replace close prices with NaN value by the corresponding reference prices
        mask = ohlc_prices["close"].isnull()
        ohlc_prices.loc[mask, "close"] = ohlc_prices.loc[mask, "reference"]

        return ohlc_prices

    def load_iboard_bulk_stock_prices(self):
        selected_fields = ["symbol", "date", "reference", "open", "high", "low", "close", "volume"]
        self.new_lines = False

        df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_price_intraday",
        )

        if not df.empty:
            df = df[selected_fields]
            logger.info(f"Load iBoard's bulk prices successfully...")

        return df

    def upload_data_frame_to_gcs(
        self,
        namespace="marketdb",
        dataset_name: str = "stock_price_ohlc_bulk_v2",
        date_str: str = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE),  # current date
        file_name: str = "stock_price_bulk.json",
    ):
        gcs_path = f"{namespace}/{dataset_name}/{date_str}/{file_name}"
        json_data = self.data_frame.to_json(orient="records", lines=True)

        gcs = GCS()
        gcs.upload_dict(dict_json=json_data, bucket_name=Config.BUCKET_NAME, gcs_path=gcs_path)

    def remove_vnd_duplicate_symbol_prices(self, symbol_prices_df: pd.DataFrame) -> pd.DataFrame:
        # get all duplicated rows of symbol
        dup_prices_df = symbol_prices_df[symbol_prices_df["date"].duplicated(keep=False)]
        dup_prices_df = dup_prices_df.sort_values(by=["date", "volume"], ascending=[False, False])

        # get duplicated dates with volume > 0
        dup_dates_vol_gt_0 = dup_prices_df.query("volume > 0")["date"]

        # get duplicated rows with volume == 0 and with the same date as rows with volume greater than 0
        removed_rows_df = dup_prices_df.query(
            "volume <= 0 and date == @dup_dates_vol_gt_0.tolist()"
        )

        # remove rows with the same date as rows with volume greater than 0
        removed_ids = removed_rows_df.index.tolist()
        dup_prices_df.drop(removed_ids, inplace=True)

        symbol_prices_df = symbol_prices_df.drop(labels=removed_ids)

        # update duplicated rows (remove rows with volume > 0 from duplicated list)
        dup_prices_df = symbol_prices_df[symbol_prices_df["date"].duplicated(keep=False)]

        # get duplicated dates with volumes == 0
        dup_dates_vol_eq_0 = list(dup_prices_df["date"].unique())
        dup_dates_vol_eq_0.sort(reverse=True)

        prev_dates = list()
        for d in dup_dates_vol_eq_0:
            date = date_str_reformat(
                input_date_str=str(d),
                date_format="%Y-%m-%d",
                to_date_format="%Y/%m/%d",
                tz=VN_TIMEZONE,
            )
            prev_date = self.get_previous_trading_date_str(date_str=date)
            prev_dates.append(prev_date)

        removed_ids = list()
        for prev_date, curr_date in zip(prev_dates, dup_dates_vol_eq_0):
            curr_rows = symbol_prices_df.query("date == @curr_date")
            prev_rows = symbol_prices_df.query("date == @prev_date")

            prev_close = prev_rows.iloc[0]["close"]
            curr_rows.loc[:, ["diff"]] = abs(curr_rows["close"] - prev_close)

            removed_ids += list(set(curr_rows.index.tolist()) - {curr_rows["diff"].idxmin()})

        symbol_prices_df = symbol_prices_df.drop(removed_ids)

        return symbol_prices_df

    def merge_historical_bulk_prices(self, input_date: str) -> pd.DataFrame:
        # load Stag bulk historical prices V2
        stag_bulk_price_df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path="marketdb/stock_price_ohlc_bulk_v2",
            input_date=input_date,
        )
        if stag_bulk_price_df.empty:
            logger.error(f"Unable to load Stag historical bulk prices V2 on {input_date}...")
            return pd.DataFrame()

        # load VNDirect bulk historical prices
        vnd_bulk_price_df = self.load(
            bucket_name=Config.BUCKET_NAME,
            base_path=f"crawler/vndirect_stock_price_bulk",
            input_date=input_date,
        )
        if vnd_bulk_price_df.empty:
            logger.error(f"Unable to load VNDirect historical bulk prices on {input_date}...")
            return pd.DataFrame()

        # load iBoard bulk historical prices
        logger.info(f"Load iBoard historical bulk prices...")
        iboard_bulk_price_df = self.load_iboard_bulk_stock_prices()

        if iboard_bulk_price_df.empty:
            logger.error(f"Unable to load iBoard historical bulk prices...")
            return pd.DataFrame()

        # get list of symbols
        symbols = (
            stag_bulk_price_df["symbol"].unique().tolist()
            + vnd_bulk_price_df["symbol"].unique().tolist()
        )
        symbols = list(set(symbols))
        symbols.sort()

        # group data source by symbol
        stag_grouped_bulk_price_df = stag_bulk_price_df.groupby("symbol")
        vnd_grouped_bulk_price_df = vnd_bulk_price_df.groupby("symbol")
        iboard_grouped_bulk_price_df = iboard_bulk_price_df.groupby("symbol")

        # merge data sources
        merged_bulk_prices_df = pd.DataFrame()
        for symbol in symbols:
            # symbol is present in Stag
            if symbol in stag_grouped_bulk_price_df.groups.keys():
                stag_symbol_prices_df = stag_grouped_bulk_price_df.get_group(symbol)
                # remove duplicated rows in symbol prices
                stag_symbol_prices_df = self.normalize_iboard_symbol_prices(
                    ohlc_prices=stag_symbol_prices_df
                )

                # symbol is present in both Stag and VNDirect
                if symbol in vnd_grouped_bulk_price_df.groups.keys():
                    # remove duplicate prices in VNDirect by symbol
                    vnd_symbol_prices_df = vnd_grouped_bulk_price_df.get_group(symbol)
                    vnd_symbol_prices_df = self.remove_vnd_duplicate_symbol_prices(
                        symbol_prices_df=vnd_symbol_prices_df
                    )

                    if len(stag_symbol_prices_df.index) >= len(vnd_symbol_prices_df.index):
                        logger.info(f"Merge prices of symbol {symbol} from Stag...")
                        merged_bulk_prices_df = pd.concat(
                            [merged_bulk_prices_df, stag_symbol_prices_df], ignore_index=True
                        )
                    else:
                        logger.info(f"Merge prices of symbol {symbol} from Stag and VNDirect...")
                        iboard_symbol_prices_df = iboard_grouped_bulk_price_df.get_group(symbol)
                        iboard_symbol_prices_df = self.normalize_iboard_symbol_prices(
                            iboard_symbol_prices_df
                        )

                        # set index as "date" to copy column "reference"
                        iboard_symbol_prices_df.set_index(keys=["date"], inplace=True)
                        vnd_symbol_prices_df.set_index(keys=["date"], inplace=True)

                        # copy column "reference" from Stag (raw iBoard) to VNDirect
                        vnd_symbol_prices_df.loc[:, ["reference"]] = iboard_symbol_prices_df[
                            "reference"
                        ]
                        vnd_symbol_prices_df.reset_index(inplace=True)
                        vnd_symbol_prices_df = vnd_symbol_prices_df[
                            [
                                "symbol",
                                "date",
                                "reference",
                                "open",
                                "high",
                                "low",
                                "close",
                                "volume",
                            ]
                        ]

                        merged_bulk_prices_df = pd.concat(
                            [merged_bulk_prices_df, vnd_symbol_prices_df], ignore_index=True
                        )

                # symbol is only present in Stag
                else:
                    merged_bulk_prices_df = pd.concat(
                        [merged_bulk_prices_df, stag_symbol_prices_df], ignore_index=True
                    )

            # symbol is not present in Stag
            else:
                # symbol is only present in VNDirect
                if symbol in vnd_grouped_bulk_price_df.groups.keys():
                    logger.info(f"Merge prices of symbol {symbol} from VNDirect...")
                    vnd_symbol_prices_df = vnd_grouped_bulk_price_df.get_group(symbol)

                    # remove duplicate prices in VNDirect by symbol
                    vnd_symbol_prices_df = self.remove_vnd_duplicate_symbol_prices(
                        symbol_prices_df=vnd_symbol_prices_df
                    )

                    merged_bulk_prices_df = pd.concat(
                        [merged_bulk_prices_df, vnd_symbol_prices_df], ignore_index=True
                    )

                # symbol is not present in both Stag and VNDirect!!!
                else:
                    logger.info(f"Stag and VNDirect doesn't have any symbol {symbol}")

        # reorder columns
        merged_bulk_prices_df = merged_bulk_prices_df[
            ["symbol", "date", "reference", "open", "high", "low", "close", "volume"]
        ]

        # reconstruct history of transactions
        merged_bulk_prices_df.sort_values(
            by=["date", "symbol"], ascending=[False, True], inplace=True, ignore_index=True
        )

        return merged_bulk_prices_df
