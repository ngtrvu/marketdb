from datetime import datetime, timedelta
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status

from api_internal.serializers.fund_nav import MutualFundNavDetailSerializer
from core.models.funds.fund_nav import MutualFundNavDaily, MutualFundNavIndex
from core.models.funds.fund_price_analytics import FundNavAnalytics
from utils.date_range import get_range_dates


class InternalMutualFundPriceDetailView(RetrieveAPIView):
    lookup_field = "symbol"
    queryset = MutualFundNavIndex.objects.all()
    serializer_class = MutualFundNavDetailSerializer
    ordering = ("symbol",)

    def get_nav_data(self, symbol, date_range):
        today = datetime.today()
        from_date, to_date = get_range_dates(date_range=date_range, to_date=today)
        queryset = MutualFundNavDaily.objects.filter(symbol=symbol.upper()).order_by("date")
        if from_date and to_date:
            queryset = queryset.filter(date__range=[from_date, to_date])
            return queryset.all()
        # only return all data for date_range = all
        elif date_range == "all":
            return queryset.all()

        return queryset.all()

    def get_object(self):
        symbol = self.kwargs.get("symbol")
        if not symbol:
            return None

        return self.queryset.filter(symbol=symbol.upper()).first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        date_range = request.GET.get("date_range", "1m")
        queryset = self.get_nav_data(instance.symbol, date_range)
        if not queryset:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        first: MutualFundNavDaily = queryset.first()
        last: MutualFundNavDaily = queryset.last()
        change_value = None
        change_percentage = None
        if first and last:
            change_value = last.nav - first.nav
            change_percentage = (change_value / first.nav) * 100 if first.nav > 0 else None

        # get performance
        symbol = self.kwargs.get("symbol")
        perf_queryset = FundNavAnalytics.objects.filter(symbol=symbol).first()
        annualized_return_percentage = annualized_return_n_year = maximum_drawdown_percentage = None
        if perf_queryset:
            annualized_return_percentage = perf_queryset.annualized_return_percentage
            annualized_return_n_year = perf_queryset.annualized_return_n_year
            maximum_drawdown_percentage = perf_queryset.maximum_drawdown_percentage

        serializer = self.get_serializer(
            instance,
            context={
                "historical_nav": queryset.all().values("date", "nav"),
                "change_value": change_value,
                "change_percentage": change_percentage,
                "date_range": date_range,
                "annualized_return_percentage": annualized_return_percentage,
                "annualized_return_n_year": annualized_return_n_year,
                "maximum_drawdown_percentage": maximum_drawdown_percentage,
            },
        )
        return Response(serializer.data)
