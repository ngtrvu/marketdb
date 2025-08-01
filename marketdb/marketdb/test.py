# Import settings from base
import os
from .base import *

DEBUG = True
TESTING_MODE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "marketdb"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        "ATOMIC_REQUESTS": True,
        "TEST": {
            "NAME": "marketdb_test",
        },
    }
}

# file storage

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
MEDIA_ROOT = "tmp/uploads"
MEDIA_URL = "tmp/uploads/"

