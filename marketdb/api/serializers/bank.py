from rest_framework import serializers

from core.models.bank import Bank


class BankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = ['id', 'title', 'slug', 'created', 'modified']


class BankDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = '__all__'


class NestedBankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = ['id', 'title', 'slug']


class BankSavingsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = [
            'savings_on_demand', 'savings_1m', 'savings_3m', 'savings_6m', 'savings_9m', 'savings_12m', 'savings_13m',
            'savings_18m', 'savings_24m', 'savings_36m',
            'online_savings_on_demand', 'online_savings_1m', 'online_savings_3m', 'online_savings_6m',
            'online_savings_9m', 'online_savings_12m', 'online_savings_13m', 'online_savings_18m',
            'online_savings_24m', 'online_savings_36m',
        ]


class BanksSavingsSerializer(serializers.ModelSerializer):
    savings_amount = serializers.SerializerMethodField()
    savings_time = serializers.SerializerMethodField()
    savings_month = serializers.SerializerMethodField()
    savings_percentage = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    savings_percentage_detail = serializers.SerializerMethodField()

    class Meta:
        model = Bank
        fields = [
            'id', 'title', 'symbol', 'market_cap', 'savings_amount', 'savings_time', 'savings_month',
            'savings_percentage', 'profit', 'total', 'non_performing_loan_ratio', 'loan_to_deposit_ratio',
            'capital_adequacy_ratio', 'savings_percentage_detail'
        ]

    def get_savings_amount(self, obj):
        return obj.savings_amount

    def get_savings_time(self, obj):
        return obj.savings_time

    def get_savings_percentage(self, obj):
        return round(obj.savings_percentage * 100, 2) if obj.savings_percentage else None

    def get_profit(self, obj):
        return obj.profit

    def get_savings_month(self, obj):
        return obj.savings_month

    def get_total(self, obj):
        return obj.total

    def get_savings_percentage_detail(self, obj):
        data = BankSavingsDetailSerializer(obj).data
        result = {}
        for key, value in data.items():
            result[key] = value * 100 if value else None

        return result
