import pandas as pd

from utils.logger import logger
from common.tinydwh.api_loader import APILoader
from common.tinydwh.data import is_nan
from common.tinydwh.datetime_util import isostring_to_datetime
from common.mdb.client import MarketdbClient


class CryptoPriceRealtimeJob(APILoader):
    marketdb_client: MarketdbClient = None

    def __init__(self):
        self.marketdb_client = MarketdbClient()

    def pipeline(self):
        # Load top 100 crypto info
        coin_items: list = self.load(
            url="https://api.coingecko.com/api/v3/coins/markets?vs_currency=vnd&order=market_cap_desc",
        )

        if not coin_items:
            logger.warning("Error: no data is loaded")
            return False

        df = pd.DataFrame(coin_items)
        items = df.apply(self.transform_row, axis=1)
        success = self.do_indexing(items.to_dict())
        if success:
            logger.info(f"CryptoPriceRealtimeJob is successfully executed")
            return True
        return False

    def transform_row(self, row: dict) -> dict:
        return {
            "symbol": row["symbol"].upper(),
            "price": row["current_price"] if not is_nan(row["current_price"]) else None,
            "market_cap": row["market_cap"] if not is_nan(row["market_cap"]) else None,
            "high": row["high_24h"] if not is_nan(row["high_24h"]) else None,
            "low": row["low_24h"] if not is_nan(row["low_24h"]) else None,
            "change_value": (
                row["price_change_24h"] if not is_nan(row["price_change_24h"]) else None
            ),
            "change_percentage": (
                row["price_change_percentage_24h"]
                if not is_nan(row["price_change_percentage_24h"])
                else None
            ),
            "market_cap_change_value": (
                row["market_cap_change_24h"]
                if not is_nan(row["market_cap_change_24h"])
                else None
            ),
            "market_cap_change_percentage": (
                row["market_cap_change_percentage_24h"]
                if not is_nan(row["market_cap_change_percentage_24h"])
                else None
            ),
            "volume": row["total_volume"] if not is_nan(row["total_volume"]) else None,
            "all_time_high": row["ath"] if not is_nan(row["ath"]) else None,
            "datetime": isostring_to_datetime(row["last_updated"]),
        }

    def do_indexing(self, items: list):
        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="CryptoPriceRealtime",
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
