from rest_framework import serializers

from core.models.market.market_analytics import FearGreedIndexDaily
from core.libs.fear_greed_index.model_config import FearGreedModelConfig


class FearGreedIndexDetailSerializer(serializers.ModelSerializer):
    prediction = serializers.SerializerMethodField()

    class Meta:
        model = FearGreedIndexDaily
        fields = '__all__'

    def get_prediction(self, obj):
        model_config = FearGreedModelConfig()
        comment, action_recommend, status = model_config.recommend_action_by_score(obj.score)
        return {
            'status': status,
            'message': comment,
            'recommendation': action_recommend,
        }


class FearGreedIndexDailyListSerializer(serializers.ModelSerializer):
    prediction = serializers.SerializerMethodField()

    class Meta:
        model = FearGreedIndexDaily
        fields = [
            'score', 'date', 'datetime', 'prediction', 'market_index', 'momentum', 'volatility', 'volatility_sma', 'rsi',
            'price_breadth'
        ]

    def get_prediction(self, obj):
        model_config = FearGreedModelConfig()
        comment, action_recommend, status = model_config.recommend_action_by_score(obj.score)
        return {
            'status': status,
        }


class NestedFearGreedIndexSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = FearGreedIndexDaily
        fields = ['score', 'status', 'date', 'datetime']

    def get_status(self, obj):
        model_config = FearGreedModelConfig()
        comment, action_recommend, status = model_config.recommend_action_by_score(obj.score)
        return status


class FearGreedIndexHistoricalValuesSerializer(serializers.Serializer):
    label = serializers.CharField()
    # date = serializers.DateField()
    fear_greed_index = NestedFearGreedIndexSerializer()
