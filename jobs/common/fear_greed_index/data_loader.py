import http
import json
from datetime import datetime
import logging
from fake_headers import Headers
import pandas as pd
from pandas import to_datetime
import requests

from common.tinydwh.datetime_util import get_delta_unix_timestamp, get_now_unix_timestamp
from common.tinydwh.storage.connector import GCS


class StockLoader:
    """Deprecated
    TODO: remove this, this is for job pipeline to handle
    """
    def __init__(self, bucket_name="stock_analytics"):
        self.history_file = "stock_price_daily.json"
        self.bucket_name = bucket_name
        self.gcs = GCS()

    def get_vn_index_ssi_url(self, index="VN30", n_day=600) -> pd.DataFrame:
        from_timestamp = get_delta_unix_timestamp(n_days=n_day)
        to_timestamp = get_now_unix_timestamp()
        host = "iboard.ssi.com.vn"
        path = f"/dchart/api/history?resolution=D&symbol={index}&from={from_timestamp}&to={to_timestamp}"
        logging.info(f"{host}, {path}")
        return host, path

    def transform_ssi_market_data(self, ohlc_json: dict):
        ohlc = pd.DataFrame(ohlc_json)

        market_df = pd.DataFrame()
        market_df['timestamp'] = ohlc['t']
        market_df['open'] = ohlc['o'].apply(float)
        market_df['high'] = ohlc['h'].apply(float)
        market_df['low'] = ohlc['l'].apply(float)
        market_df['close'] = ohlc['c'].apply(float)
        market_df['volume'] = ohlc['v'].apply(float)
        market_df['datetime'] = market_df['timestamp'].apply(datetime.utcfromtimestamp)
        market_df['datetime'] = to_datetime(market_df['datetime'], format='%d-%m-%Y')

        market_df.index = market_df['datetime']
        market_df.sort_index(inplace=True)
        market_df.drop_duplicates(subset='datetime', inplace=True)

        market_df['change'] = market_df['close'].diff()
        market_df['pct_change'] = market_df['close'].pct_change()

        logging.debug(f"Df Head {market_df.head()}")
        logging.debug(f"Df tail {market_df.tail()}")
        logging.debug(f"Total day {len(market_df)}")

        return market_df

    def transform_market_ohlc_bulk(self, ohlc_json: dict):
        ohlc = pd.DataFrame(ohlc_json)

        market_df = pd.DataFrame()
        market_df['timestamp'] = ohlc['timestamp']
        market_df['open'] = ohlc['open'].apply(float)
        market_df['high'] = ohlc['high'].apply(float)
        market_df['low'] = ohlc['low'].apply(float)
        market_df['close'] = ohlc['close'].apply(float)
        market_df['volume'] = ohlc['volume'].apply(float)
        market_df['datetime'] = market_df['timestamp'].apply(datetime.utcfromtimestamp)
        market_df['datetime'] = to_datetime(market_df['datetime'], format='%d-%m-%Y')

        market_df.index = market_df['datetime']
        market_df.sort_index(inplace=True)
        market_df.drop_duplicates(subset='datetime', inplace=True)

        market_df['change'] = market_df['close'].diff()
        market_df['pct_change'] = market_df['close'].pct_change()

        logging.debug(f"Df Head {market_df.head()}")
        logging.debug(f"Df tail {market_df.tail()}")
        logging.debug(f"Total day {len(market_df)}")

        return market_df

    def get_local_json(self, file_path):
        f = open(file_path)
        return json.load(f)

    def get_all_stock_prices(self) -> str:
        """Load stock price data exported from postgres
        """
        file_path = "marketdb/market_index_ohlc_bulk/market_index_ohlc_daily.json"
        data = self.gcs.get_json_data(bucket_name=self.bucket_name, gcs_path=file_path)

        return data

    def get_vn_index_data(self, load_gcs=True, n_day=600, index_symbol="VN30"):
        if load_gcs:
            response_data = self.get_all_stock_prices()
            response_json = response_data

            index_df = self.transform_market_ohlc_bulk(response_json)
            return index_df[index_df['symbol'] == index_symbol]

        host, path = self.get_vn_index_ssi_url(index=index_symbol, n_day=n_day)
        header = Headers(
            browser="chrome",  # Generate only Chrome UA
            os="win",  # Generate ony Windows platform
            headers=True  # generate misc headers
        )

        conn = http.client.HTTPSConnection(host)
        payload = ''
        conn.request("GET", path, payload, header.generate())
        res = conn.getresponse()

        response_data = res.read()
        if response_data:
            try:
                response_json = json.loads(response_data)
            except Exception as e:
                print(f"StockLoader error : {e}")
                response_json = []

            return self.transform_ssi_market_data(response_json)
        return None
