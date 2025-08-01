import os
import time
import unittest
from unittest.mock import patch

from gcp_storage_emulator.server import create_server
from google.cloud import storage

from common.utils.server import get_free_port
from common.utils.singleton import Singleton


class GcsEmulator(Singleton):

    def __init__(self):
        port = get_free_port()
        self._server = create_server("localhost", port, in_memory=False)
        os.environ["STORAGE_EMULATOR_HOST"] = f"http://localhost:{port}"

    def start(self):
        if not self._server._api.is_alive():
            self._server.start()
            time.sleep(1)

    def stop(self):
        self._server.wipe()
        self._server.stop()
        time.sleep(1)


class GcsTestCase:
    bucket: storage.Bucket
    client: storage.Client
    bucket_name: str = "gcs-test-bucket"
    project_name: str = "test-project"

    def setUpBucket(self, bucket_name: str):
        try:
            self.bucket: storage.Bucket = self.client.create_bucket(bucket_name)
        except Exception as e:
            self.bucket: storage.Bucket = self.client.bucket(bucket_name)
        
    def setUp(self, bucket_name):
        self.client = storage.Client(project=self.project_name)
        self.setUpBucket(bucket_name)

    @classmethod
    def setUpClass(cls):
        cls.gcs_emulator = GcsEmulator()
        cls.gcs_emulator.start()

    @classmethod
    def tearDownClass(cls):
        cls.gcs_emulator.stop()
