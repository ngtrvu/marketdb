from django.urls import include, path, re_path
from rest_framework import routers

from api_internal.views.etf_price import InternalETFPriceDetailView
from api_internal.views.fund_analytics import FundAnalyticsDetailView
from api_internal.views.fund_nav import InternalMutualFundPriceDetailView
from api_internal.views.market_calendar import MarketCalendarView
from api_internal.views.etf_price import InternalETFPriceChartView
from api_internal.views.stock import StockViewSet

app_name = "api_public"

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"stocks", StockViewSet, basename="stock")
router.register(r"etf-price-charts", InternalETFPriceChartView, basename="etf-price-chart")

urlpatterns = [
    # check calendars
    re_path(
        r"^market-calendar/(?P<date>[0-9-]+)",
        MarketCalendarView.as_view(),
        name="market-calendar-detail",
    ),
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
