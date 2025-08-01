from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from api_admin.serializers.market_calendar import MarketCalendarDetailSerializer
from core.models.market.market_calendar import MarketCalendar, MarketStatusEnum
from core.services.open_trading.check_calendar import CheckCalendarService


class MarketCalendarView(RetrieveAPIView):
    queryset = MarketCalendar.objects.all()
    serializer_class = MarketCalendarDetailSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    lookup_field = 'date'
    ordering = ('-date',)

    def retrieve(self, request, *args, **kwargs):
        date_str = self.kwargs['date']
        try:
            service = CheckCalendarService(date=date_str)
            is_trading_date = service.call()
            market_status = MarketStatusEnum.OPEN if is_trading_date else MarketStatusEnum.CLOSE
            calendar: MarketCalendar = service.get_data()
            if calendar:
                description = calendar.description
            else:
                description = "Ngày giao dịch" if is_trading_date else "Ngày cuối tuần không giao dịch"
        except Exception as ex:
            return Response(data={'error': service.get_error_message()}, status=status.HTTP_400_BAD_REQUEST)

        instance = MarketCalendar(date=date_str, status=market_status, description=description)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
