# Import settings from base
from .base import *
import os

DEBUG = True

STATIC_URL = '/static/'
STATIC_ROOT = 'static'

MEDIA_URL = os.environ.get('MEDIA_URL', '/')
MEDIA_ROOT = 'uploads'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'marketdb'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
    }
}

CORS_ALLOW_ALL_ORIGINS = True

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

INSTALLED_APPS += ["debug_toolbar", "drf_yasg"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]