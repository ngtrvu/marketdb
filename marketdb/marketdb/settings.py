"""
Django settings for marketdb project.
Generated by 'django-admin startproject' using Django 4.0.5.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import logging
import os

from common.utils.logger import setup_logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get ENV variable from environment variable or default :development
ENV = os.environ.get("ENV")
if ENV == "production" or ENV == "development":
    setup_logger(level=os.environ.get("LOG_LEVEL", "INFO"))

    from marketdb.prod import *
else:
    import sys

    TESTING = sys.argv[1:2] == ["test"]
    if TESTING:
        setup_logger(level="CRITICAL")
        logging.disable(logging.CRITICAL)

        from marketdb.test import *
    else:
        from marketdb.local import *
