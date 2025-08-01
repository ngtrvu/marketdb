import enum
from common.utils.logger import logger

from django.db import connection
from google.cloud import storage

from common.utils.datetime_util import VN_TIMEZONE, get_date_str


class DatetimeFlags(enum.Enum):
    NO_DATETIME = "NO_DATETIME"


class DjExporter(object):

    def get_file_blob(self, bucket_name, file_path):
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        return bucket.blob(file_path)

    def export_table_to_gcs(
        self,
        bucket_name: str,
        dataset_name: str,
        table_name: str,
        directory_name: str = None,
        input_date: str = None,
    ):
        if not input_date:  # get default by today
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        sql = f"""
        SELECT row_to_json({table_name})
        FROM {table_name} 

        """
        output_query = f"""
        COPY ({sql}) TO STDIN
        """

        if not directory_name:
            directory_name = table_name

        if input_date == DatetimeFlags.NO_DATETIME.value:
            file_path = f"{dataset_name}/{directory_name}/{table_name}.json"
        else:
            file_path = f"{dataset_name}/{directory_name}/{input_date}/{table_name}.json"

        try:
            with connection.cursor() as cursor:
                blob = self.get_file_blob(bucket_name=bucket_name, file_path=file_path)
                with blob.open("w") as f:
                    cursor.copy_expert(output_query, f)

            logger.info(f"save {table_name} to file on GCS: gs://{bucket_name}/{file_path}")
            return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False
