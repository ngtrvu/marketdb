from django.db.models import F, Case, Value, When, DecimalField

from core.services.base import BaseService
from core.services.bank.get_banks import GetBanksService
from core.models.bank import Bank


class GetBanksSavingsService(BaseService):

    SAVINGS_TIME_MAPPING = {
        "savings_1m": 1,
        "savings_3m": 3,
        "savings_6m": 6,
        "savings_9m": 9,
        "savings_12m": 12,
        "savings_13m": 13,
        "savings_18m": 18,
        "savings_24m": 24,
        "savings_36m": 36,
        "online_savings_1m": 1,
        "online_savings_3m": 3,
        "online_savings_6m": 6,
        "online_savings_9m": 9,
        "online_savings_12m": 12,
        "online_savings_13m": 13,
        "online_savings_18m": 18,
        "online_savings_24m": 24,
        "online_savings_36m": 36,
    }

    def __init__(self, savings_amount, savings_time, limit=10):
        self.savings_amount = savings_amount
        self.savings_time = savings_time
        self.limit = limit

    def is_valid(self) -> bool:
        if not self.savings_amount and self.savings_amount <= 0:
            self.error_message = "Savings amount should be greater than zero"

        if not self.savings_time or not self.SAVINGS_TIME_MAPPING.get(self.savings_time):
            self.error_message = "Savings time is invalid"

        return True

    def call(self):
        if not self.is_valid():
            return None

        savings_amount = float(self.savings_amount)
        savings_time = self.savings_time
        savings_month = self.SAVINGS_TIME_MAPPING.get(savings_time)

        queryset = GetBanksService().call()

        queryset = queryset.annotate(
            savings_amount=Value(savings_amount),
            savings_time=Value(savings_time),
            savings_percentage=F(savings_time),
            savings_month=Value(savings_month),
            profit=Case(
                When(
                    savings_percentage__isnull=True,
                    then=None,
                ),
                default=F("savings_amount") * F("savings_percentage") * F("savings_month") / 12,
                output_field=DecimalField()
            ),
            total=Case(
                When(
                    savings_percentage__isnull=True,
                    then=None,
                ),
                default=F("profit") + F("savings_amount"),
                output_field=DecimalField()
            ),
        )

        queryset = queryset.order_by(F('savings_percentage').desc(nulls_last=True))
        if self.limit and self.limit > 0:
            ids = queryset[:self.limit].values_list('id', flat=True)
            queryset = queryset.filter(id__in=list(ids))

        return queryset
