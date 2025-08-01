from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response

from common.utils.datetime_util import get_datetime_now, VN_TIMEZONE
from core.services.open_trading.check_calendar import CheckCalendarService
from core.services.open_trading.get_trading_order_type import GetTradingOrderTypeService, DEFAULT_SYMBOL


class MarketOpenTradingView(RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        datetime_obj = get_datetime_now(tz=VN_TIMEZONE)
        trading_date = datetime_obj.strftime('%Y-%m-%d')

        is_trading_date = CheckCalendarService(date=trading_date).call()
        datetime_obj = get_datetime_now(tz=VN_TIMEZONE)
        today_0900 = datetime_obj.replace(hour=9, minute=0, second=0)
        today_1500 = datetime_obj.replace(hour=15, minute=00, second=0)
        is_open_trading = is_trading_date and (today_0900 <= datetime_obj <= today_1500)
        message = "Trong giờ giao dịch" if is_open_trading else "Ngoài giờ giao dịch"

        return Response({
            "item": {
                "is_open_trading": is_open_trading,
                "is_open_trading_date": is_trading_date,
                "is_trading_date_valid": is_trading_date,  # Deprecated
                "trading_date": trading_date,
                "message": message
            }
        }, status=status.HTTP_200_OK)


class TradingOrderView(ListAPIView):
    def list(self, request, *args, **kwargs):
        symbol = self.request.GET.get('symbol', '')
        trading_orders = GetTradingOrderTypeService(symbol=symbol).call()

        return Response({"items": trading_orders}, status=status.HTTP_200_OK)
