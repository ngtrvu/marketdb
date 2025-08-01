from rest_framework import serializers

from core.models.funds.fund_nav import MutualFundNavIndex
from api.serializers.fund import MutualFundSerializer

HISTORICAL_DATE_RANGES = ["1m", "3m", "1y", "3y", "5y"]


class MutualFundNavSerializer(serializers.ModelSerializer):
    fund = MutualFundSerializer()
    class Meta:
        model = MutualFundNavIndex
        fields = "__all__"


class MutualFundNavDetailSerializer(serializers.ModelSerializer):
    change_percentage = serializers.SerializerMethodField()
    change_value = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField()
    date_ranges = serializers.SerializerMethodField()
    date_range = serializers.SerializerMethodField()
    annualized_return_percentage = serializers.SerializerMethodField()
    annualized_return_n_year = serializers.SerializerMethodField()
    maximum_drawdown_percentage = serializers.SerializerMethodField()

    class Meta:
        model = MutualFundNavIndex
        fields = [
            "symbol",
            "nav",
            "total_nav",
            "datetime",
            "date",
            "change_percentage",
            "change_value",
            "prices",
            "date_ranges",
            "date_range",
            "annualized_return_percentage",
            "annualized_return_n_year",
            "maximum_drawdown_percentage",

        ]

    def get_date_range(self, obj):
        return self.context.get("date_range", "1m")

    def get_change_percentage(self, obj):
        return self.context.get("change_percentage")

    def get_change_value(self, obj):
        return self.context.get("change_value")

    def get_prices(self, obj):
        historical_data = self.context.get("historical_nav")
        return NavItemSerializer(historical_data, many=True).data

    def get_date_ranges(self, obj):
        return HISTORICAL_DATE_RANGES

    def get_annualized_return_percentage(self, obj):
        return self.context.get("annualized_return_percentage")

    def get_annualized_return_n_year(self, obj):
        return self.context.get("annualized_return_n_year")

    def get_maximum_drawdown_percentage(self, obj):
        return self.context.get("maximum_drawdown_percentage")


class NavItemSerializer(serializers.Serializer):
    nav = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    date = serializers.DateField(required=True)
