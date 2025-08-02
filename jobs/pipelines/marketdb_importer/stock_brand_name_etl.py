import pandas as pd

from common.tinydwh.base import MiniJobBase
from utils.logger import logger
from common.tinydwh.storage.utils import load_json
from common.mdb.client import (
    MarketdbClient,
)
from config import Config


class StockBrandNameETL(MiniJobBase):
    data_frame: pd.DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.brand_names = None
        self.sampling_ratio = sampling_ratio
        self.marketdb_client = MarketdbClient()

    def load_df_brand_names(self, bucket_name: str, base_path: str):
        logger.info(f"Loading data from bucket {bucket_name} {base_path}")
        df = pd.read_json(
            load_json(bucket_name=bucket_name, source=base_path), lines=True
        )

        df = df[["brand_name", "symbol"]]

        # convert data frames to list of dictionaries
        self.brand_names = df.to_dict("records")

    def pipeline(self):
        self.load_df_brand_names(
            bucket_name=Config.BUCKET_NAME,
            base_path="crawler/vietstock/company_brand_name/collected_brand_name.json",
        )

        success_indexing = self.do_indexing(self.brand_names)
        if success_indexing:
            logger.info(f"StockInfoETL is successfully executed")
            return True

        return False

    def do_indexing(self, items: list):

        try:
            success, response = self.marketdb_client.index_to_db_bulk(
                model_name="Stock",
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
