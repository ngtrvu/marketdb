import pandas as pd

from common.tinydwh.api_loader import APILoader
from common.tinydwh.data import is_nan
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)


class CryptoInfoETL(APILoader):
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
        success = self.do_indexing(items.to_list())
        if success:
            logger.info(f"CryptoInfoETL is successfully executed")
            return True

        return False

    def transform_row(self, row: dict) -> dict:
        return {
            "symbol": row["symbol"].upper(),
            "name": row["name"],
            "coingecko_id": row["id"],
            # i.e. image = https://assets.coingecko.com/coins/images/1/large/bitcoin.png?1547033579
            "photo": row["image"].replace(
                "https://assets.coingecko.com/coins/images", "//coingecko_assets"
            ),
            "market_cap_rank": row["market_cap_rank"],
            "market_cap": row["market_cap"] if not is_nan(row["market_cap"]) else None,
            "fully_diluted_valuation": (
                row["fully_diluted_valuation"]
                if not is_nan(row["fully_diluted_valuation"])
                else None
            ),
            "circulating_supply": (
                row["circulating_supply"]
                if not is_nan(row["circulating_supply"])
                else None
            ),
            "total_supply": (
                row["total_supply"] if not is_nan(row["total_supply"]) else None
            ),
            "max_supply": row["max_supply"] if not is_nan(row["max_supply"]) else None,
            "status": 1002,
        }

    def do_indexing(self, items: list):
        logger.info("Set all coins to draft, make sure coins are out of the top 100")
        success, response = self.marketdb_client.bulk_update(
            model_name="Crypto", values={"status": 1001}, conditions={"status": 1002}
        )

        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="Crypto",
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
