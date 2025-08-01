import json
import logging
from datetime import date

import pandas as pd
from google.cloud import bigquery, storage


def generate_bq_sql(sql_file_path: str, params: dict) -> str:

    if not sql_file_path:
        raise ValueError("sql_file_path is required")

    with open(sql_file_path, "r") as f:
        sql_str = f.read()

        for key, value in params.items():
            logging.debug(f"{key}:{value}")
            if value:
                sql_str = sql_str.replace(key, value)
        return sql_str


def run_bq(sql_file_path: str, params: dict) -> bool:
    if not sql_file_path:
        raise ValueError("sql_file_path is required")

    sql_str = generate_bq_sql(sql_file_path=sql_file_path, params=params)

    try:
        client = bigquery.Client()
        client.query_and_wait(sql_str)
        logging.info(f"Query {sql_file_path} completed successfully...")
    except Exception as ex:
        logging.error(f"Query {sql_file_path} failed with error: {ex}")
        return False

    return True

def excute_bq(sql_file_path: str, params: dict, to_df: bool=False):
    if not sql_file_path:
        raise ValueError("sql_file_path is required")

    sql_str = generate_bq_sql(sql_file_path=sql_file_path, params=params)

    try:
        client = bigquery.Client()
        query_job = client.query(sql_str)
        result = query_job.result()  # Wait for the job to complete.

        if to_df:
            df = result.to_dataframe()  # Convert the result to a DataFrame.
            logging.info(f"Query {sql_file_path} completed successfully and returned a DataFrame.")
            return True, df
        else:
            logging.info(f"Query {sql_file_path} completed successfully.")
            return True, pd.DataFrame()
    except Exception as ex:
        logging.error(f"Query {sql_file_path} failed with error: {ex}")
        if to_df:
            return (False, pd.DataFrame())  # Return an empty DataFrame in case of error
        else:
            return (False, pd.DataFrame())

def export_bq_to_gcs(sql_str: str, destination_uri: str, project_id: str, dataset_id: str, table_id: str):
    client = bigquery.Client(project=project_id)

    # Define the query job
    query_job = client.query(sql_str)
    logging.info(f"Executing query: {sql_str}")

    # Wait for the query to complete
    results = query_job.result()

    # Transform the results into a list of records
    records = []
    for row in results:
        record = dict(row)
        for key, value in record.items():
            if isinstance(value, date):
                record[key] = value.isoformat()
        records.append(record)

    # Convert the records to JSON format
    json_data = json.dumps(records)

    # Upload the JSON data to GCS
    storage_client = storage.Client()
    bucket_name, blob_name = destination_uri.replace("gs://", "").split("/", 1)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(json_data, content_type="application/json")

    logging.info(f"Exported {project_id}.{dataset_id}.{table_id} to {destination_uri}")