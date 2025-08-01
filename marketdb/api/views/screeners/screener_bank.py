from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView

from common.drfexts.filters.ordering import OrderingFilter
from common.drfexts.serializers.filters import FilterSerializer
from api.serializers.bank import BanksSavingsSerializer
from api.serializers.screener import ScreenerSerializer
from core.services.bank.get_banks import GetBanksService
from core.services.bank.get_banks_savings import GetBanksSavingsService


class ScreenerBanksViewSet(ListAPIView):
    serializer_class = ScreenerSerializer

    def get_queryset(self):
        serializer = FilterSerializer(data=self.request.GET.dict())
        if not serializer.is_valid():
            raise ValueError("Request params invalid")

        fields, filters, sorts = (
            serializer.validated_data.get("fields", []),
            serializer.validated_data.get("filters", []),
            serializer.validated_data.get("sorts", []),
        )
        self.queryset = GetBanksService(fields=fields, filters=filters, sorts=sorts).call()
        return self.queryset


class GetBanksSavingsViewSet(ListAPIView):
    serializer_class = BanksSavingsSerializer
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )

    def get_queryset(self):
        savings_amount = self.request.GET.get("savings_amount", None)
        savings_time = self.request.GET.get("savings_time", None)
        input_limit = self.request.GET.get("limit", 10)
        limit = 10
        if input_limit and str(input_limit).isnumeric():
            limit = int(input_limit)

        savings_month = GetBanksSavingsService.SAVINGS_TIME_MAPPING.get(savings_time)
        if not savings_amount or not savings_time or not savings_month:
            raise ValidationError(detail="savings_amount or savings_time is invalid")

        self.queryset = GetBanksSavingsService(
            savings_amount=savings_amount, savings_time=savings_time, limit=limit
        ).call()
        return self.queryset
