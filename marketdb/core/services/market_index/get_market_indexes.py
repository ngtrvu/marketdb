from core.services.product import ProductService
from core.models.market_index.market_index import MarketIndex
from core.models.market_index.market_index_analytics import MarketIndexAnalytics


class GetMarketIndexesService(ProductService):

    main_model = MarketIndex
    meta_models = [MarketIndexAnalytics]
    join_field = 'symbol'
    mapping_fields = {}

    fields = []
    filters = []
    sorts = []
