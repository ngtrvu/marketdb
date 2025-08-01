from rest_framework import serializers


class BenchmarkingSerializer(serializers.Serializer):
    stocks = serializers.CharField(max_length=500, required=False)
    etfs = serializers.CharField(max_length=500, required=False)
    mutual_funds = serializers.CharField(max_length=500, required=False)
    industries = serializers.CharField(max_length=500, required=False)
    market_indexes = serializers.CharField(max_length=500, required=False)
    criteria = serializers.CharField(max_length=500, required=True)

    def validate_stocks(self, value):
        return value.split(',') if value else []

    def validate_etfs(self, value):
        return value.split(',') if value else []

    def validate_mutual_funds(self, value):
        return value.split(',') if value else []

    def validate_industries(self, value):
        return value.split(',') if value else []

    def validate_market_indexes(self, value):
        return value.split(',') if value else []

    def validate_criteria(self, value):
        return value
