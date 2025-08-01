import json
import os

from common.utils.logger import logger, setup_logger
from google.cloud import storage


setup_logger(level=os.environ.get("LOG_LEVEL", "INFO"))


class GCS:
    def __init__(self):
        self.storage_client = storage.Client()

    def __call__(self):
        return self.storage_client

    def upload_dict(self, dict_json: dict, bucket_name: str, gcs_path: str):
        logger.debug(f"Upload dict json to bucket gs://{bucket_name}/{gcs_path}")
        
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        return blob.upload_from_string(data=dict_json, content_type="application/json")

    def upload_file(self, local_path: str, bucket_name: str, gcs_path: str):
        logger.info(f"Upload file to bucket gs://{bucket_name}/{gcs_path}")

        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        return blob.upload_from_filename(local_path)

    def download_file(self, local_path, bucket_name, gcs_path):
        pass

    def list_files(self, bucket_name, gcs_path, max_results=None):
        logger.info(f"Listing files in bucket gs://{bucket_name}/{gcs_path}")

        if not bucket_name or not gcs_path:
            return []

        files = []
        for blob in self.storage_client.list_blobs(
            bucket_name, prefix=gcs_path, max_results=max_results
        ):
            if not blob.name.endswith("/"):
                # get list files only
                files.append(blob.name)
        return files

    def get_json_data(self, bucket_name: str, gcs_path: str):
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        json_data_string = blob.download_as_string()
        json_data = json.loads(json_data_string)

        return json_data

    def load_json(self, bucket_name: str, gcs_path: str) -> str:
        if not bucket_name:
            raise ValueError("Not found bucket_name in config")

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.get_blob(gcs_path)

        if not blob:
            return None

        json_data_string = blob.download_as_string().decode("utf-8")
        return json_data_string

    def upload_to_gcs(self, dict_data: dict, bucket_name: str, gcs_path: str):
        self.upload_dict(
            dict_json=json.dumps(dict_data), bucket_name=bucket_name, gcs_path=gcs_path
        )
