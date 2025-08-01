# Import settings from base
import logging
import os

from .base import *

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "marketdb"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "CONN_MAX_AGE": 120,
        "PORT": "5432",
        "TEST": {"NAME": "test_marketdb"},
        "ATOMIC_REQUESTS": True,
    }
}

RAVEN_CONFIG = {
    "dsn": "https://:@sentry.io/280769",
}

CORS_ALLOW_ALL_ORIGINS = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = "/www/marketdb/static/"

MEDIA_URL = os.environ.get("MEDIA_URL", "/")
MEDIA_ROOT = "/www/marketdb/uploads/"

LOGGING_LEVEL = "INFO" if os.environ.get("ENV") == "production" else "DEBUG"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "gunicorn": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "gunicorn.errors": {
            "level": "WARNING",
            "handlers": ["gunicorn", "console"],
            "propagate": True,
        },
        "django": {
            "level": "WARNING",
            "handlers": ["gunicorn", "console"],
            "propagate": True,
        },
        "django.request": {
            "handlers": ["gunicorn", "console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

if SERVICE_MONITOR == "yes":
    # Prometheus settings
    MIDDLEWARE = (
        ["django_prometheus.middleware.PrometheusBeforeMiddleware"]
        + MIDDLEWARE
        + ["django_prometheus.middleware.PrometheusAfterMiddleware"]
    )

    INSTALLED_APPS += ["django_prometheus"]

    PROMETHEUS_METRICS_EXPORT_PORT_RANGE = [9090, 9091]
    PROMETHEUS_METRICS_EXPORT_ADDRESS = ""  # all addresses
    PROMETHEUS_EXPORT_MIGRATIONS = False
