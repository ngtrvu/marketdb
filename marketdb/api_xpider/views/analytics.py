from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from api_xpider.serializers.analytics import AnalyticsSerializer, SentimentSerializer


class AnalyticsViewSet(ReadOnlyModelViewSet):
    serializer_class = AnalyticsSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AnalyticsSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        # serializer = self.get_serializer(queryset, many=True)

        import random
        from datetime import datetime
        d1 = datetime.now()
        random.seed(d1.hour)

        negative_percentage = random.uniform(51, 61)
        negative_percentage = round(negative_percentage, 0)
        sentiment_ratio = {
                    'negative_percentage': negative_percentage,
                    'positive_percentage': 100 - negative_percentage
                }
        sentiment_serializer = SentimentSerializer(
                data=sentiment_ratio, many=False
            )
        sentiment_serializer.is_valid()

        serializer = AnalyticsSerializer(
            data={'sentiment_ratio': sentiment_ratio}, many=False
        )
        serializer.is_valid()

        return Response(data=serializer.data, status=status.HTTP_200_OK)
        # return Response(data={"error": service.get_error_message()},
        #                 status=status.HTTP_404_NOT_FOUND)
