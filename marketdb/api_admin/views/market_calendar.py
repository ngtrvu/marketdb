from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from common.auth.google import GoogleAuthentication
from api_admin.serializers.market_calendar import (
    MarketCalendarCreateSerializer,
    MarketCalendarDetailSerializer,
    MarketCalendarSerializer,
    MarketCalendarUpdateSerializer,
)
from core.models.market.market_calendar import MarketCalendar


class MarketCalendarViewSet(viewsets.ModelViewSet):
    queryset = MarketCalendar.objects.all()
    serializer_class = MarketCalendarSerializer
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = "__all__"
    ordering = ("-date",)
    authentication_classes = [GoogleAuthentication]

    def get_serializer_class(self):
        if self.action == "create":
            return MarketCalendarCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return MarketCalendarUpdateSerializer
        elif self.action == "retrieve":
            return MarketCalendarDetailSerializer
        return self.serializer_class
