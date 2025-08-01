from django.urls import include, path, re_path
from rest_framework import routers

from api_internal.views.admin import (
    InternalBankViewSet,
    InternalCollectionGroupViewSet,
    InternalCollectionViewSet,
    InternalCryptoViewSet,
    InternalIndustryViewSet,
    InternalMutualFundViewSet,
    InternalStockEventViewSet,
    InternalStockPriceRealtimeViewSet,
)
from api_internal.views.etf import ETFViewSet
from api_internal.views.etf_price import InternalETFPriceDetailView
from api_internal.views.fund_analytics import FundAnalyticsDetailView
from api_internal.views.fund_nav import InternalMutualFundPriceDetailView
from api_internal.views.indexer import BulkIndexerView, IndexerView
from api_internal.views.market_calendar import MarketCalendarView
from api_internal.views.market_index import MarketIndexViewSet
from api_internal.views.models import BulkUpdateView
from api_internal.views.search_index import SearchReindexingView
from api_internal.views.stock import StockViewSet
from api_internal.views.stock_event import StockEventDeleteView
from api_internal.views.xpider import PageViewSet, PublisherViewSet
from api_internal.views.exporter import TableExporterView
from api_internal.views.etf_price import InternalETFPriceChartView

from api_internal.views.intraday import (
    IntradayInitializerView,
    IntradayIndexerView,
    IntradayDetailView,
)

app_name = "api_internal"

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"banks", InternalBankViewSet)
router.register(r"collections", InternalCollectionViewSet)
router.register(r"collection-groups", InternalCollectionGroupViewSet)
router.register(r"cryptos", InternalCryptoViewSet)
router.register(r"etfs", ETFViewSet, basename="etf")
router.register(r"etf-price-charts", InternalETFPriceChartView, basename="etf-price-chart")
router.register(r"funds", InternalMutualFundViewSet)
router.register(r"industries", InternalIndustryViewSet)
router.register(r"market-indexes", MarketIndexViewSet, basename="market-index")
router.register(r"stock-events", InternalStockEventViewSet)
router.register(
    r"stock-price-realtimes",
    InternalStockPriceRealtimeViewSet,
    basename="stock-price-realtime",
)
router.register(r"stocks", StockViewSet, basename="stock")
router.register(r"xpider-pages", PageViewSet, basename="xpider-page")
router.register(r"xpider-publishers", PublisherViewSet, basename="xpider-publisher")

urlpatterns = [
    # check calendars
    re_path(
        r"^market-calendar/(?P<date>[0-9-]+)",
        MarketCalendarView.as_view(),
        name="market-calendar-detail",
    ),
    # indexer
    re_path(
        r"^indexer/bulk-update", BulkUpdateView.as_view(), name="indexer-bulk-update"
    ),
    re_path(
        r"^indexer/stock-events/delete",
        StockEventDeleteView.as_view(),
        name="stock-events-delete",
    ),
    re_path(r"^indexer/bulk", BulkIndexerView.as_view(), name="bulk-data-indexer"),
    re_path(r"^indexer", IndexerView.as_view(), name="data-indexer"),
    # exporter
    re_path(r"^exporter/table", TableExporterView.as_view(), name="table-exporter"),
    # intraday
    re_path(
        r"^intraday/initialize",
        IntradayInitializerView.as_view(),
        name="intraday-initializer",
    ),
    re_path(r"^intraday/index", IntradayIndexerView.as_view(), name="intraday-indexer"),
    re_path(
        r"^intraday/keys/(?P<symbol>[0-9a-zA-Z\-]+)",
        IntradayDetailView.as_view(),
        name="intraday-detail",
    ),
    # search-index
    re_path(
        r"^search-index/reindex", SearchReindexingView.as_view(), name="search-reindex"
    ),
    # etfs
    re_path(
        r"^etfs/(?P<symbol>[0-9a-zA-Z\-]+)/prices$",
        InternalETFPriceDetailView.as_view(),
        name="etf-price-detail",
    ),
    # funds
    re_path(
        r"^funds/(?P<symbol>[0-9a-zA-Z\-]+)/prices$",
        InternalMutualFundPriceDetailView.as_view(),
        name="mutual-fund-price-detail",
    ),
    re_path(
        r"^funds/(?P<symbol>[0-9a-zA-Z\-]+)/analytics$",
        FundAnalyticsDetailView.as_view({"get": "retrieve"}),
        name="fund-price-analytics",
    ),
    path(r"", include(router.urls)),
]
