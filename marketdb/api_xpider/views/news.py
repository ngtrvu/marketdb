from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from xpider.models.news import NewsPost
from api_xpider.serializers.news import NewsPostSerializer, \
    NewsPostDetailSerializer, NewsTopicSerializer
from xpider.services.news_topic_service import NewsTopicService
from xpider.services.news_post import GetNewsPostService
from xpider.services.news_trending_service import \
    NewsTrendingService


class NewsPostViewSet(ReadOnlyModelViewSet):
    lookup_field = "uuid"
    serializer_class = NewsPostSerializer
    queryset = GetNewsPostService().get_queryset()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filterset_fields = ['language', 'category']
    ordering = ('-published',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NewsPostDetailSerializer
        return self.serializer_class


class NewsTopicViewSet(ReadOnlyModelViewSet):
    lookup_field = "uuid"
    serializer_class = NewsTopicSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter,)
    filterset_fields = ['language', 'category']
    ordering = ('-published',)

    def get_queryset(self):
        topic_token = self.kwargs.get('topic', None)
        service = NewsTopicService(topic_token=topic_token)
        if service.call():
            self.queryset = service.get_data()
        self.queryset = NewsPost.objects.none()
        return self.queryset

    def list(self, request, *args, **kwargs):
        topic_token = self.request.GET.get('topic', '')
        service = NewsTopicService(topic_token=topic_token)

        if service.call():
            queryset = self.filter_queryset(service.get_data())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)

            resp = self.get_paginated_response(serializer.data)
            return resp

        return Response(data={"error": service.get_error_message()},
                        status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NewsPostDetailSerializer
        elif self.action == 'list':
            return NewsTopicSerializer
        return self.serializer_class


class NewsTrendingViewSet(ReadOnlyModelViewSet):
    serializer_class = NewsTopicSerializer
    ordering = ('-published',)

    def get_queryset(self):
        limit = self.kwargs.get('limit', 10)
        service = NewsTrendingService(limit=limit)
        if service.call():
            self.queryset = service.get_data()
        self.queryset = NewsPost.objects.none()
        return self.queryset

    def list(self, request, *args, **kwargs):
        limit = self.kwargs.get('limit', 10)
        service = NewsTrendingService(limit=limit)

        if service.call():
            queryset = self.filter_queryset(service.get_data())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)

            resp = self.get_paginated_response(serializer.data)
            return resp

        return Response(data={"error": service.get_error_message()},
                        status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):
        if self.action == 'list':
            return NewsTopicSerializer
        return self.serializer_class
