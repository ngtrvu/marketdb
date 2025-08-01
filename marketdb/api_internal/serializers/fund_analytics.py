from rest_framework import serializers

from core.models.funds.fund_price_analytics import FundNavAnalytics


class FundAnalyticsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundNavAnalytics
        fields = "__all__"
        singular_resource_name = "item"
