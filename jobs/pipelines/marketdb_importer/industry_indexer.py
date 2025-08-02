from pandas import DataFrame
from slugify import slugify

from common.tinydwh.data import is_nan
from utils.logger import logger
from common.mdb.client import (
    MarketdbClient,
)


class IndustryIndexer:

    def __init__(self):
        self.marketdb_client = MarketdbClient()

    def do_indexing(self, df: DataFrame):
        items = df.to_dict(orient="records")

        # import industry data
        for item in items:
            item_id = int(item.get("id"))
            data = {
                "name": item.get("name"),
                "description": item.get("description"),
                "photo": item.get("photo"),
                "slug": item.get("code", slugify(item.get("name"))),
                "level": item.get("level"),
                "icb_code": item.get("icb_code"),
                "status": 1002,
            }
            if item_id:
                success, response = self.marketdb_client.update_or_create(
                    model_name="Industry",
                    key_name="id",
                    key_value=item_id,
                    payload=data,
                )
                if not success:
                    logger.error(f"Industry update item error: {response}")

        # update parents
        for item in items:
            item_id = int(item.get("id"))
            parent = item.get("parent_id")
            parent_id = int(parent) if parent and not is_nan(parent) else 0
            if item_id and parent_id:
                success, response = self.marketdb_client.update_or_create(
                    model_name="Industry",
                    key_name="id",
                    key_value=item_id,
                    payload={"parent_id": parent_id},
                )

                if not success:
                    logger.error(f"Industry update error: {response}")
