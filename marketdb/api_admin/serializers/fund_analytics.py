from rest_framework import serializers

from core.models.funds.fund_price_analytics import FundNavAnalytics


class FundAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundNavAnalytics
        fields = [
            'symbol',
            'nav',
            'annualized_return_percentage',
            'annualized_return_n_year',
            'maximum_drawdown_percentage',
        ]
        singular_resource_name = "item"


class FundAnalyticsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundNavAnalytics
        fields = "__all__"
        singular_resource_name = "item"
