import io
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import json
import math

import pandas as pd
from joblib import Parallel, delayed
from pandas import DataFrame
from tqdm import tqdm

from common.tinydwh.sampling import GCSSampling
from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str, str_to_datetime
from common.tinydwh.date_ranges import DateRangeUtils
from utils.logger import logger
from common.tinydwh.storage.connector import GCS
from common.tinydwh.storage.utils import get_blobs


class MiniJobBase:
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0
    backfill_dates: list[str] = []  # ['2022/12/01', '2022/11/30']
    new_lines: bool = True
    parallel: int = 5
    custom_dtype = {}

    def __init__(self, new_lines: bool = True):
        self.new_lines = new_lines

    def sampling(self, bucket_name, base_path):
        gcs_sampling = GCSSampling(
            bucket_name=bucket_name, base_path=base_path, ratio=self.sampling_ratio
        )
        items = gcs_sampling.get_sampling()
        for path in items:
            json_data = gcs_sampling.get_data_from_path(path)
            self.data_frame = pd.concat([self.data_frame, pd.DataFrame([json_data])])
        return {"message": f"Process {gcs_sampling.count} rows successfully"}

    def fill_row_na(self, row: dict):
        filled_row = {}
        for key, val in row.items():
            if type(val) == float and math.isnan(val):
                filled_row[key] = None
            else:
                filled_row[key] = val
        return filled_row

    def df_to_json_newlined(self, ds: pd.Series):
        df = pd.DataFrame(ds.to_list())
        return df.to_json(orient="records", lines=True)

    def ensure_json(self, json_str: str):
        json_str = json_str.replace('\\"', '"').strip()

        if self.new_lines:
            return json_str

        if json_str.startswith("{") and json_str.endswith("}"):
            json_str = f"[{json_str}]"

        return json_str

    def load_blobs(
        self, base_path, bucket_name: str, input_date: str = "", file_name_prefix: str = ""
    ):
        dir_path = f"{base_path}"

        if input_date:
            dir_path = f"{dir_path}/{input_date}"
        else:
            dir_path = f"{dir_path}/"

        if file_name_prefix:
            dir_path = dir_path.strip("/")
            dir_path = f"{dir_path}/{file_name_prefix}"

        logger.debug(f"Loading data from bucket {bucket_name} {dir_path}")

        blobs = get_blobs(bucket_name=bucket_name, source=dir_path)
        if not blobs:
            error = f"Cannot get blobs from GCS. dir_path: {dir_path}, bucket_name: {bucket_name}"

            logger.error(error)
            raise Exception(error)

        return blobs

    def load(
        self, base_path: str, bucket_name: str, input_date: str = "", file_name_prefix: str = ""
    ):
        blobs = self.load_blobs(
            base_path=base_path,
            bucket_name=bucket_name,
            input_date=input_date,
            file_name_prefix=file_name_prefix,
        )
        self.data_frame = pd.DataFrame()
        success_rows = 0
        count = 0

        for blob in blobs:
            try:
                json_str = self.ensure_json(blob.download_as_bytes().decode("utf-8"))
                if not json_str:
                    continue
                
                if bool(self.custom_dtype):
                    df = pd.read_json(json_str, lines=self.new_lines, dtype=self.custom_dtype)
                else:
                    df = pd.read_json(json_str, lines=self.new_lines)

                success_rows += len(df.index)
                self.data_frame = pd.concat([self.data_frame, df])
                count += 1
            except Exception as error:
                logger.error("Get blob error: {0}".format(str(error)))
                return pd.DataFrame()

        logger.debug(f"Load {success_rows} rows successfully")

        return self.data_frame

    def load_csv(
            self, base_path: str, bucket_name: str, input_date: str = "", file_name_prefix: str = ""
    ):
        blobs = self.load_blobs(
            base_path=base_path,
            bucket_name=bucket_name,
            input_date=input_date,
            file_name_prefix=file_name_prefix,
        )
        self.data_frame = pd.DataFrame()
        success_rows = 0
        count = 0

        for blob in blobs:
            try:
                csv_str = blob.download_as_bytes()
                if not csv_str:
                    continue

                df = pd.read_csv(io.BytesIO(csv_str))

                success_rows += len(df.index)
                self.data_frame = pd.concat([self.data_frame, df])
                count += 1
            except Exception as error:
                logger.error("Get blob error: {0}".format(str(error)))
                return pd.DataFrame()
        logger.debug(f"Load {success_rows} rows successfully")

        return self.data_frame

    def load_json(
        self,
        base_path: str,
        bucket_name: str,
        input_date: str = "",
        file_name_prefix: str = "",
        nested_fields: list[str] = None,
        key_field: str = "",
    ):
        if nested_fields and not key_field:
            raise Exception("key_field is required when setting nested_fields")

        blobs = self.load_blobs(
            base_path=base_path,
            bucket_name=bucket_name,
            input_date=input_date,
            file_name_prefix=file_name_prefix,
        )

        data_frame = pd.DataFrame()
        success_rows = 0
        count = 0
        for blob in blobs:
            try:
                json_str = blob.download_as_bytes().decode("utf-8")
                if not json_str:
                    continue

                json_data = json.loads(json_str)
                df = pd.DataFrame()
                for nested_field in nested_fields:
                    df_i = pd.json_normalize(json_data.get(nested_field))
                    if df.empty:
                        df = df_i
                    else:
                        df = df.merge(df_i, on=key_field, how="left")

                data_frame = pd.concat([data_frame, df])
                success_rows += len(df.index)
                count += 1
            except Exception as error:
                logger.error("Get blob error: {0}".format(str(error)))
                return pd.DataFrame()

        logger.info(f"Load {success_rows} rows successfully")
        return data_frame

    def pipeline(self, input_date: str = "") -> bool:
        raise NotImplementedError()

    def run(self, **kwargs):
        # if your pipeline did not run success, please return false
        try:
            success = self.pipeline(**kwargs)
        except Exception as error:
            logger.error("Pipeline error: {0}".format(str(error)))
            logger.exception("Pipeline error: {0}".format(str(error)))
            success = False

        if success:
            return 0

        exit(1)

    def load_backfill_dates(self, input_date: str = None, from_date: str = None) -> list:
        utils = DateRangeUtils()
        to_date_obj = str_to_datetime(input_str=input_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        from_date_obj = str_to_datetime(input_str=from_date, date_format="%Y/%m/%d", tz=VN_TIMEZONE)
        return utils.get_dates_by_range(from_date_obj, to_date_obj, date_format="%Y/%m/%d", tz=VN_TIMEZONE)

    def filter_backfill_dates(self, input_date: str = ""):
        """
        Filter out dates which not in the historical time range given by input_date
        :param input_date:
        :return: new backfill dates
        """
        dates = []
        datetime_obj = str_to_datetime(input_date, date_format="%Y/%m/%d")
        for backfill_date in self.backfill_dates:
            if str_to_datetime(backfill_date, date_format="%Y/%m/%d") <= datetime_obj:
                dates.append(backfill_date)
        return dates

    def run_backfilling(self, input_date: str = None, from_date: str = None):
        """
        Backfill util for pipeline, currently support only on backfilling on datetime
        :param from_date: start date for backfilling
        :param input_date: the current date of the job
        :return:
        """
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.backfill_dates = self.load_backfill_dates(input_date, from_date)

        logger.info(
            f"Run backfilling {len(self.backfill_dates)} date(s) in {self.parallel} parallel jobs..."
        )
        logger.info(f"Dates {self.backfill_dates}")
        results = Parallel(n_jobs=self.parallel)(
            delayed(self.pipeline)(backfill_date) for backfill_date in tqdm(self.backfill_dates)
        )

        logger.info(f"Complete backfilling {results}")

    def export_to_gcs(self, df: pd.DataFrame, bucket_name: str, gcs_path: str):
        logger.info(f"Exporting data to {bucket_name}: {gcs_path}...")

        try:
            json_data = df.to_json(orient="records", lines=True)
            GCS().upload_dict(dict_json=json_data, bucket_name=bucket_name, gcs_path=gcs_path)
            return True
        except Exception as error:
            logger.error(f"Export to GCS error: {error}")
            return False
