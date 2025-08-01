from django.urls import path, re_path, include

from rest_framework import routers

from api_admin.views.collection import (
    CollectionViewSet, CollectionGroupViewSet, CollectionMetricsView, CollectionOperatorsView
)
from api_admin.views.fund_analytics import FundAnalyticsDetailViewSet
from api_admin.views.fund_nav import MutualFundPriceDetailView
from api_admin.views.industry import IndustryViewSet
from api_admin.views.bank import BankViewSet
from api_admin.views.stock import StockViewSet
from api_admin.views.stock_analytics import StockFAViewSet
from api_admin.views.stock_event import StockEventViewSet, StockEventLogViewSet
from api_admin.views.etf import ETFViewSet
from api_admin.views.fund import MutualFundViewSet
from api_admin.views.crypto import CryptoViewSet


app_name = 'api_admin'

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'collections', CollectionViewSet)
router.register(r'collection-groups', CollectionGroupViewSet)
router.register(r'industries', IndustryViewSet)
router.register(r'banks', BankViewSet)
router.register(r'stocks', StockViewSet)
router.register(r'stock-fas', StockFAViewSet)
router.register(r'stock-events', StockEventViewSet)
router.register(r'stock-event-logs', StockEventLogViewSet)
router.register(r'etfs', ETFViewSet)
router.register(r'cryptos', CryptoViewSet)
router.register(r'funds', MutualFundViewSet, basename='fund')

urlpatterns = [
    re_path(
        r'^collections/(?P<product_type>[0-9a-zA-Z_]+)/metrics',
        CollectionMetricsView.as_view(),
        name='collection-metrics',
    ),
    re_path(
        r'^collections/(?P<product_type>[0-9a-zA-Z_]+)/operators',
        CollectionOperatorsView.as_view(),
        name='collection-operators',
    ),
    # funds
    re_path(
        r"^funds/(?P<symbol>[0-9a-zA-Z\-]+)/prices",
        MutualFundPriceDetailView.as_view(),
        name="mutual-fund-price-detail",
    ),
    re_path(
        r"^funds/(?P<symbol>[0-9a-zA-Z\-]+)/analytics",
        FundAnalyticsDetailViewSet.as_view({'get': 'retrieve'}),
        name="fund-price-analytics",
    ),

    path(r'', include(router.urls)),
]
