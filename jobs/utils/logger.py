import json
import os
import sys
from logging import getLevelName

from loguru import logger as loguru_logger

PY_LOG_FORMAT = "%(asctime)s | %(levelname)s | [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s"


def setup_logger(level: str):
    loguru_logger.remove()

    # Local Logging (GKE, GCE, ...):
    loguru_logger.add(sys.stdout, level=level)

    # Cloud Logging
    if os.environ.get("CLOUD_LOGGING_ENABLED") == "True":
        import google.cloud.logging
        from google.cloud.logging_v2.handlers import CloudLoggingHandler

        client = google.cloud.logging.Client()
        handler = CloudLoggingHandler(client, name="gcp-logger")
        handler.setLevel(level=getLevelName(level))


logger = loguru_logger
