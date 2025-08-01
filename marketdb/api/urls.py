from django.urls import path, re_path, include

from rest_framework import routers

from api.views.collection import (
    CollectionViewSet,
    CollectionItemsView,
    CollectionsByContentTypeView,
)
from api.views.watchlist_collection import WatchlistCollectionViewSet
from api.views.etf import ETFViewSet
from api.views.funds.fund import MutualFundViewSet
from api.views.funds.fund_nav import MutualFundNavViewset
from api.views.funds.fund_nav_v1 import MutualFundPriceDetailView
from api.views.screeners.screener_bank import (
    ScreenerBanksViewSet,
    GetBanksSavingsViewSet,
)
from api.views.screeners.screener_etf import ScreenerETFsViewSet
from api.views.screeners.screener_fund import ScreenerFundsViewSet
from api.views.screeners.screener_stock import ScreenerStocksViewSet
from api.views.screeners.screener_industry import ScreenerIndustriesViewSet
from api.views.screeners.screener_market_index import (
    ScreenerMarketIndexesViewSet,
)
from api.views.search import SearchView
from api.views.index.market_index import MarketIndexViewSet
from api.views.index.market_index_value import MarketIndexValueViewSet
from api.views.etfs.etf_price import ETFPriceDetailView
from api.views.etfs.etf_price_intraday import ETFOrderStatsView
from api.views.stocks.stock import StockViewSet
from api.views.stocks.stock_analytics import (
    StockFAViewSet,
    StockScoringView,
)
from api.views.stocks.stock_price_chart import StockPriceChartView
from api.views.stocks.stock_price_intraday import StockOrderStatsView
from api.views.stocks.stock_price_realtime import (
    StockPriceRealtimeDetailView,
)
from api.views.stocks.stock_trending import TrendingStockView
from api.views.cryptos.crypto import CryptoViewSet
from api.views.cryptos.crypto_price_realtime import (
    CryptoPriceRealtimeDetailView,
)
from api.views.trending import MarketTrendingView
from api.views.etfs.etf_trending import ETFTrendingView
from api.views.open_trading import MarketOpenTradingView, TradingOrderView
from api.views.analytics.fear_greed_index import (
    FearGreedIndexView,
    FearGreedIndexDailyListView,
    FearGreedIndexHistoricalValuesView,
)
from api.views.industry import IndustryViewSet
from api.views.benchmarking import BenchmarkingView

app_name = "api"

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"stocks", StockViewSet, basename="stocks")
router.register(r"indexes", MarketIndexViewSet, basename="indexes")
router.register(r"market-index", MarketIndexValueViewSet, basename="market-index")
router.register(r"etfs", ETFViewSet, basename="etfs")
router.register(r"funds", MutualFundViewSet, basename="funds")
router.register(r"fund-nav", MutualFundNavViewset, basename="fund-nav")
router.register(r"cryptos", CryptoViewSet, basename="cryptos")
router.register(r"collections", CollectionViewSet, basename="collections")
router.register(r"industries", IndustryViewSet, basename="industries")
router.register(
    r"watchlist-collections",
    WatchlistCollectionViewSet,
    basename="watchlist-collections",
)

urlpatterns = [
    re_path(
        r"^stocks/(?P<symbol>[0-9a-zA-Z]+)/prices$",
        StockPriceRealtimeDetailView.as_view(),
        name="stock-price-realtime-detail",
    ),
    re_path(
        r"^stocks/(?P<symbol>[0-9a-zA-Z]+)/charts$",
        StockPriceChartView.as_view(),
        name="stock-price-chart",
    ),
    re_path(
        r"^stocks/(?P<symbol>[0-9a-zA-Z]+)/order-stats$",
        StockOrderStatsView.as_view(),
        name="stock-order-stats",
    ),
    re_path(
        r"^stocks/(?P<symbol>[0-9a-zA-Z]+)/fundamental$",
        StockFAViewSet.as_view(),
        name="stock-fundamental",
    ),
    re_path(
        r"^stocks/(?P<symbol>[0-9a-zA-Z]+)/scoring$",
        StockScoringView.as_view(),
        name="stock-scoring-detail",
    ),
    # collect the realtime price from the exchange on a same db from StockPriceRealtime,
    # including stocks, etfs, indexes, and derivatives
    # ETFs
    re_path(
        r"^etfs/(?P<symbol>[0-9a-zA-Z]+)/prices$",
        ETFPriceDetailView.as_view(),
        name="etf-price-realtime-detail",
    ),
    re_path(
        r"^etfs/(?P<symbol>[0-9a-zA-Z]+)/order-stats$",
        ETFOrderStatsView.as_view(),
        name="etf-order-stats",
    ),
    # funds
    re_path(
        r"^funds/(?P<symbol>[0-9a-zA-Z\-]+)/prices$",
        MutualFundPriceDetailView.as_view(),
        name="mutual-fund-price-detail",
    ),
    # cryptos
    re_path(
        r"^cryptos/(?P<symbol>[0-9a-zA-Z]+)/prices$",
        CryptoPriceRealtimeDetailView.as_view(),
        name="crypto-price-realtime-detail",
    ),
    # indexes
    re_path(
        r"^indexes/(?P<symbol>[0-9a-zA-Z]+)/prices$",
        StockPriceRealtimeDetailView.as_view(),
        name="index-realtime-detail",
    ),
    re_path(r"benchmarking$", BenchmarkingView.as_view(), name="benchmarking"),
    # screener
    re_path(
        r"^screener/stocks$", ScreenerStocksViewSet.as_view(), name="screener-stocks"
    ),
    re_path(r"^screener/etfs$", ScreenerETFsViewSet.as_view(), name="screener-etfs"),
    re_path(r"^screener/funds$", ScreenerFundsViewSet.as_view(), name="screener-funds"),
    re_path(r"^screener/banks$", ScreenerBanksViewSet.as_view(), name="screener-banks"),
    re_path(
        r"^screener/industries",
        ScreenerIndustriesViewSet.as_view(),
        name="screener-industries",
    ),
    re_path(
        r"^screener/market-indexes",
        ScreenerMarketIndexesViewSet.as_view(),
        name="screener-market-indexes",
    ),
    re_path(r"^banks/savings$", GetBanksSavingsViewSet.as_view(), name="savings-banks"),
    # trending items
    re_path(
        r"^stocks/trending$",
        TrendingStockView.as_view({"get": "list"}),
        name="trending-stocks",
    ),
    re_path(
        r"^market/trending$",
        MarketTrendingView.as_view({"get": "list"}),
        name="trending-market",
    ),
    re_path(
        r"^etfs/trending$",
        ETFTrendingView.as_view({"get": "list"}),
        name="trending-etfs",
    ),
    re_path(
        r"^market/open-trading",
        MarketOpenTradingView.as_view(),
        name="check-open-trading",
    ),
    re_path(r"^market/trading-order", TradingOrderView.as_view(), name="trading-order"),
    # analytics
    re_path(
        r"^market/fear-greed-index$",
        FearGreedIndexView.as_view(),
        name="fear-greed-index",
    ),
    re_path(
        r"^market/fear-greed-index/charts$",
        FearGreedIndexDailyListView.as_view(),
        name="fear-greed-index-daily",
    ),
    re_path(
        r"^market/fear-greed-index/historical-values$",
        FearGreedIndexHistoricalValuesView.as_view(),
        name="fear-greed-index-historical-values",
    ),
    # collections
    re_path(
        r"^collections/contents/(?P<content_type>[0-9a-zA-Z]+)",
        CollectionsByContentTypeView.as_view(),
        name="collections-by-content-type",
    ),
    re_path(
        r"^collections/(?P<collection_id>[0-9]+)/items$",
        CollectionItemsView.as_view(),
        name="collection-detail-items",
    ),
    # search
    re_path(r"^search$", SearchView.as_view(), name="search"),
    path(r"", include(router.urls)),
]
