from core.services.product import ProductService
from core.models.stocks.stock import Stock
from core.models.stocks.stock_analytics import StockFA
from core.models.stocks.stock_price_chart import StockPriceChart
from core.models.stocks.stock_price_analytics import StockPriceAnalytics
from core.models.stocks.stock_price_realtime import StockPriceRealtime


class GetStocksService(ProductService):

    main_model = Stock
    meta_models = [StockFA, StockPriceChart, StockPriceRealtime, StockPriceAnalytics]
    join_field = 'symbol'
    mapping_fields = {}
    override_mapping_fields = {
        'change_percentage_1d': StockPriceAnalytics,
        'change_percentage_1w': StockPriceAnalytics,
        'change_percentage_1m': StockPriceAnalytics,
        'change_percentage_3m': StockPriceAnalytics,
        'change_percentage_6m': StockPriceAnalytics,
        'change_percentage_1y': StockPriceAnalytics,
        'change_percentage_3y': StockPriceAnalytics,
        'change_percentage_5y': StockPriceAnalytics,
        'change_percentage_ytd': StockPriceAnalytics,
    }

    fields = []
    filters = []
    sorts = []
