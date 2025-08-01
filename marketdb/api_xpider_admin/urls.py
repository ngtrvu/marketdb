from django.urls import path, include

from rest_framework import routers

from api_xpider_admin.views.news import NewsPostViewSet
from api_xpider_admin.views.industry import IndustryViewSet

app_name = 'api_admin'

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'posts', NewsPostViewSet, basename='posts')
router.register(r'industries', IndustryViewSet, basename='industries')

urlpatterns = [
    path(r'', include(router.urls)),
]
