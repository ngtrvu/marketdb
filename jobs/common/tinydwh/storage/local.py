import json
import glob
import logging

from common.gcs.base import StorageBase


class LocalStorage(StorageBase):

    def __init__(self):
        pass

    def get_blobs(self, path: str, ext: str = "json") -> list:
        try:
            return glob.glob(f"{path}/**/*.{ext}", recursive=True)
        except Exception as error:
            logging.error("Access GCS error: ".format(str(error)))
            return []


