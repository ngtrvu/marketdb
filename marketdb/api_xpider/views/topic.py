from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from xpider.models.news import Topic
from api_xpider.serializers.topic import TopicSerializer, \
    TopicDetailSerializer


class TopicsViewSet(ReadOnlyModelViewSet):
    lookup_field = "uuid"
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filterset_fields = ['type']
    ordering = ('topic_token',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TopicDetailSerializer
        return self.serializer_class
