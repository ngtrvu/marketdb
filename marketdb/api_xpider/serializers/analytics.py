from rest_framework import serializers


class AnalyticsSerializer(serializers.Serializer):
    sentiment_ratio = serializers.JSONField(allow_null=True)
    # news_sentiment = serializers.SerializerMethodField()

    # class Meta:
    #     fields = [
    #         'news_sentiment'
    #     ]


class SentimentSerializer(serializers.Serializer):
    negative_percentage = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    positive_percentage = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    # t = TimestampField(required=True)  # timestamp in integer
