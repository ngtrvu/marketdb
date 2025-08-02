"""marketdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.urls import include, path, re_path

from common.drfexts.views.monitor import (
    health_check,
    ready_check,
)

urlpatterns = [
    path("healthy", health_check, name="health-check"),
    path("ready", ready_check, name="ready-check"),

    # TODO: Add internal API with JWT auth
    # re_path(
    #     r"^marketdb-internal/v1/",
    #     include("api_internal.urls", namespace="api_internal"),
    # ),
    re_path(
        r"^marketdb-public/v1/",
        include("api_public.urls", namespace="api_public"),
    ),
    re_path(
        r"^marketdb-api/admin/v1/",
        include("api_admin.urls", namespace="api_admin"),
    ),
    re_path(
        r"^marketdb-api/app/v1/", include("api.urls", namespace="api")
    ),
    re_path(
        r"^marketdb-api/xpider/v1/",
        include("api_xpider.urls", namespace="api_xpider"),
    ),
    re_path(
        r"^marketdb-api/xpider-admin/v1/",
        include("api_xpider_admin.urls", namespace="api_xpider_admin"),
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
elif settings.SERVICE_MONITOR == "yes":
    urlpatterns += [
        path("", include("django_prometheus.urls")),
    ]
