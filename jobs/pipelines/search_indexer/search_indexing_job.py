from utils.logger import logger
from common.tinydwh.base import MiniJobBase
from common.mdb.client import MarketdbClient


class SearchIndexingJob(MiniJobBase):
    """
    This is for indexing values for search. Currently, we support stock, ETFs
    """

    def __init__(self, sampling_ratio: float = 1.0):
        self.marketdb_client = MarketdbClient()

    def pipeline(self, input_date=None):
        success, data = self.marketdb_client.reindex_search_index()
        if success:
            logger.info("SearchIndexingJob: Stock indexes are indexed successfully")
        else:
            logger.warning(f"SearchIndexingJob failed: {data}")
            return False
        
        return True
