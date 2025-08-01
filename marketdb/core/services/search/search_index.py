from __future__ import unicode_literals

from django.contrib.postgres.search import SearchVector
from django.db import models
from slugify import slugify
from common.utils.logger import logger

from core.models.mixin import ContentStatusEnum
from core.models.search_index import SearchIndex
from core.models.stocks.stock import Stock
from core.models.etfs.etf import ETF
from core.services.base import BaseService


def generate_search_vector(symbol: str, name: str, brand_name: str):
    start_words = "{0} {1}".format(symbol[0:2], symbol[0:1])

    normalize_name = slugify(name).replace("-", " ")
    if brand_name:
        normalize_brand_name = slugify(brand_name).replace("-", " ")
    else: 
        normalize_brand_name = ""
    
    search_name = "{0} {1} {2} {3}".format(
        name, normalize_name, brand_name, normalize_brand_name
    )

    vector_symbol = SearchVector(models.Value(symbol), weight="A", config="simple")
    vector_start_words = SearchVector(
        models.Value(start_words), weight="B", config="simple"
    )
    vector_chunk_symbol = SearchVector(
        models.Value(symbol.replace("", "*").strip()), weight="C", config="simple"
    )
    vector_name = SearchVector(models.Value(search_name), weight="D")

    return vector_symbol + vector_start_words + vector_chunk_symbol + vector_name


class SearchReindexService(BaseService):

    def __init__(self):
        self

    def call(self) -> bool:
        result = self.clear_search_index()
        if not result:
            return False

        stock_result = self.stock_reindex()
        etf_result = self.etf_reindex()

        return stock_result and etf_result

    def clear_search_index(self):
        try:
            SearchIndex.objects.all().delete()
        except Exception as ex:
            logger.warning(ex)
            self.error_message = f"Search index clearing failed: {ex}"
            return False
        return True

    def stock_reindex(self):
        try:
            items = Stock.objects.filter(
                status=ContentStatusEnum.PUBLISHED, exchange_status=Stock.STATUS_LISTED
            )
            for item in items:
                search_vector = generate_search_vector(
                    item.symbol, item.name, item.brand_name
                )
                SearchIndex.objects.update_or_create(
                    symbol=item.symbol,
                    defaults={
                        "name": item.name,
                        "brand_name": item.brand_name,
                        "photo": item.photo,
                        "type": "stock",
                        "search_vector": search_vector,
                    },
                )
        except Exception as ex:
            logger.warning(ex)
            self.error_message = f"Search re-indexing stock failed: {ex}"
            return False

        return True
    
    def etf_reindex(self):
        try:
            items = ETF.objects.filter(
                status=ContentStatusEnum.PUBLISHED, exchange_status=Stock.STATUS_LISTED
            )
            for item in items:
                search_vector = generate_search_vector(item.symbol, item.name, "")
                SearchIndex.objects.update_or_create(
                    symbol=item.symbol,
                    defaults={
                        "name": item.name,
                        "brand_name": item.symbol,
                        "photo": item.photo,
                        "type": "etf",
                        "search_vector": search_vector,
                    },
                )
        except Exception as ex:
            logger.warning(ex)
            self.error_message = f"Search re-indexing etf failed: {ex}"
            return False

        return True
