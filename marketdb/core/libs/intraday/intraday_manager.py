import logging
import os
from datetime import datetime

import pytz
from redis import Redis

from common.utils.datetime_util import (
    VN_TIMEZONE,
    get_datetime_now,
    get_now_unix_timestamp,
)
from common.redis.redis_cache import init_redis_pool


def convert_timestamp_in_datetime_utc(timestamp_received):
    dt_naive_utc = datetime.utcfromtimestamp(timestamp_received)
    return dt_naive_utc.replace(tzinfo=pytz.utc)


class IntradayManager:
    """Stores and Retrieves timeseries data from Redis"""

    ts_key_pattern = "ts:{symbol}:{field_name}"
    key_pattern = "stock:{symbol}:{field_name}"
    expire_second = 60 * 60 * 24 * 5  # default expire key 5 days
    price_field = "price"
    volume_field = "volume"
    timestamp_field = "timestamp"
    ts_db = "intraday"
    is_ato_time = False
    reference_price = 0.0

    def __init__(
        self, redis_connection: Redis = None, expire_second: int = 0, write_mode=False
    ):
        if not redis_connection:
            redis_host = os.environ.get(
                "REDIS_STACK_HOST", "redis-stack-server.marketdb"
            )
            redis_connection = init_redis_pool(redis_host=redis_host)

        self._redis = redis_connection
        if expire_second > 0:
            self.expire_second = expire_second
        if write_mode:
            try:
                # create ts database
                self._redis.ts().create(self.ts_db, retension_msecs=10)
            except Exception as e:
                print(f"TS.CREATE {e}")

    def get_all_keys(self, prefix: str):
        return self._redis.keys(prefix)

    def init_ato_time(self, reference_price: float):
        self.reference_price = reference_price
        self.is_ato_time = True

    def initialize(self):
        """Initialize trading date: clear all previous trading date's values.

        :return:
        """
        logging.info("Initialize trading date...")
        pipe = self._redis.pipeline()

        keys = self.get_all_keys(prefix="ts:*")
        logging.info(f"Reset all TS keys by yesterday: {len(keys)} keys...")

        start_day_dt = get_datetime_now(tz=VN_TIMEZONE).replace(
            hour=0, minute=0, second=0
        )
        start_day_ts = get_now_unix_timestamp(datetime_obj=start_day_dt, tz=VN_TIMEZONE)
        for key in keys:
            pipe.execute_command("ts.del", key, 0, start_day_ts)

        try:
            pipe.execute()
        except Exception as ex:
            logging.debug(ex)

        keys = self.get_all_keys(prefix="quote:*")
        logging.info(f"Reset all quote keys: {len(keys)} keys...")
        for key in keys:
            try:
                pipe.execute_command("del", key, 0)
                pipe.execute()
            except Exception as ex:
                logging.debug(ex)

    def add_price(self, symbol: str, timestamp: int, price: float):
        pipe = self._redis.pipeline()

        price_key: str = self.key_pattern.format(
            symbol=symbol, field_name=self.price_field
        )
        timestamp_key: str = self.key_pattern.format(
            symbol=symbol, field_name=self.timestamp_field
        )
        pipe.set(price_key, price)
        pipe.set(timestamp_key, timestamp)

        return pipe.execute()

    def get_price(self, symbol: str):
        price_key: str = self.key_pattern.format(
            symbol=symbol, field_name=self.price_field
        )
        timestamp_key: str = self.key_pattern.format(
            symbol=symbol, field_name=self.timestamp_field
        )

        if not self._redis:
            return None, None

        price = self._redis.get(price_key)
        timestamp = self._redis.get(timestamp_key)
        if not price or not timestamp:
            return None, None
        return float(price), float(timestamp)

    def get_prices(self, symbols: list):
        if not self._redis:
            return {}

        result = {}
        for symbol in symbols:
            price_key: str = self.key_pattern.format(
                symbol=symbol, field_name=self.price_field
            )
            timestamp_key: str = self.key_pattern.format(
                symbol=symbol, field_name=self.timestamp_field
            )

            price = self._redis.get(price_key)
            timestamp = self._redis.get(timestamp_key)
            if not price or not timestamp:
                result[symbol] = {
                    "price": None,
                    "timestamp": None,
                }
            else:
                result[symbol] = {
                    "price": float(price),
                    "timestamp": float(timestamp),
                }

        return result

    def add_ts(self, symbol: str, timestamp: int, price: float, volume: int):
        pipe = self._redis.pipeline()
        pipe.execute_command(
            "ts.add",
            self.ts_key_pattern.format(symbol=symbol, field_name=self.price_field),
            timestamp,
            price,
            "last",
        )
        pipe.execute_command(
            "ts.add",
            self.ts_key_pattern.format(symbol=symbol, field_name=self.volume_field),
            timestamp,
            volume,
            "last",
        )
        # set expire
        pipe.execute_command(
            "expire",
            self.ts_key_pattern.format(symbol=symbol, field_name=self.price_field),
            self.expire_second,
        )
        pipe.execute_command(
            "expire",
            self.ts_key_pattern.format(symbol=symbol, field_name=self.volume_field),
            self.expire_second,
        )

        # Execute pipeline
        return pipe.execute()

    def get_latest(self, symbol, field_name: str):
        ts_key = self.ts_key_pattern.format(symbol=symbol, field_name=field_name)
        return self._redis.ts().get(ts_key)

    def get_range(self, symbol, field_name: str, from_time, to_time) -> list:
        ts_key = self.ts_key_pattern.format(symbol=symbol, field_name=field_name)
        return self._redis.ts().range(ts_key, from_time, to_time)

    def get_and_build_chart_matching(self, symbol):
        pass

    def get_and_build_chart_1d(self, symbol, ts_age_second=60 * 60 * 8) -> list:
        try:
            latest_ts, latest_price = self.get_latest(
                symbol=symbol, field_name=self.price_field
            )
            from_ts = latest_ts - ts_age_second
            price_key = self.ts_key_pattern.format(
                symbol=symbol, field_name=self.price_field
            )
            prices = self._redis.ts().range(price_key, from_ts, latest_ts)

            results = []
            if self.is_ato_time and self.reference_price > 0:
                price = self.reference_price
                start_day_dt = get_datetime_now().replace(hour=2, minute=0, second=0)
                results.append(
                    {
                        "o": None,
                        "h": None,
                        "l": None,
                        "c": float(price),
                        "t": start_day_dt,
                    }
                )

            for idx, tp in enumerate(prices):
                ts, price = tp

                results.append(
                    {
                        "o": None,
                        "h": None,
                        "l": None,
                        "c": float(price),
                        "t": convert_timestamp_in_datetime_utc(ts),
                    }
                )

            return results

        except Exception as e:
            logging.debug(f"{symbol}: {e}")
            return []

    def get_and_build_chart_intraday(self, symbol, ts_age_second=60 * 60 * 8) -> dict:
        # ts_age_second is 8 hour from the latest price
        try:
            latest_ts, latest_price = self.get_latest(
                symbol=symbol, field_name=self.price_field
            )
            from_ts = latest_ts - ts_age_second
            price_key = self.ts_key_pattern.format(
                symbol=symbol, field_name=self.price_field
            )
            prices = self._redis.ts().range(price_key, from_ts, latest_ts)

            volume_key = self.ts_key_pattern.format(
                symbol=symbol, field_name=self.volume_field
            )
            volumes = self._redis.ts().range(volume_key, from_ts, latest_ts)

            price_volume_agg = {}
            for idx, tp in enumerate(prices):
                ts, price = tp
                ts2, volume = volumes[idx]
                if float(price) not in price_volume_agg:
                    price_volume_agg[float(price)] = volume
                else:
                    price_volume_agg[float(price)] += volume
            return price_volume_agg
        except Exception as e:
            logging.debug(f"{symbol}: {e}")
            return {}
