from django.urls import path, re_path, include

from rest_framework import routers

from api_xpider.views.analytics import AnalyticsViewSet
from api_xpider.views.news import (
    NewsPostViewSet, NewsTopicViewSet, NewsTrendingViewSet)
from api_xpider.views.topic import TopicsViewSet

app_name = 'api'

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'posts', NewsPostViewSet, basename='posts')
router.register(r'topics', TopicsViewSet, basename='topics')

urlpatterns = [
    # remove later
    re_path(r'^news$',
            NewsTopicViewSet.as_view({'get': 'list'}),
            name='news-topic'),
    # support search by topic/symbol and more ...
    re_path(r'^posts/filter$',
            NewsTopicViewSet.as_view({'get': 'list'}),
            name='news-filter'),
    re_path(r'^posts/trending$',
            NewsTrendingViewSet.as_view({'get': 'list'}),
            name='news-trending'),
    # market news analytics
    re_path(r'^analytics/news$',
            AnalyticsViewSet.as_view({'get': 'retrieve'}),
            name='analytics-news'),

    path(r'', include(router.urls)),
]
