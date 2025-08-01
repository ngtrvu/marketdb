import json
import glob
import logging


class StorageBase:

    def __init__(self):
        pass

    def upload_file(self, source, destination):
        pass

    def upload_json(self, data, destination):
        pass

    def get_json(self, source):
        pass

    def load_json(self, source) -> str:
        pass

    def get_blobs(self, path: str, ext: str = "json") -> list:
        pass


