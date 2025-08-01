import json

from google.cloud import storage


def upload_file(bucket_name, source, destination):
    if not bucket_name:
        raise ValueError("Not found bucket_name in config")

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination)
    blob.upload_from_filename(source)
    
    return blob


def upload_json(bucket_name, data, destination):
    if not bucket_name:
        raise ValueError("Not found bucket_name in config")

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination)
    blob.upload_from_string(data)

    return blob


def get_json(bucket_name, source):
    if not bucket_name:
        raise ValueError("Not found bucket_name in config")

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(source)

    if not blob:
        return None

    json_data_string = blob.download_as_string()
    json_data = json.loads(json_data_string)

    return json_data


def load_json(bucket_name, source) -> str:
    if not bucket_name:
        raise ValueError("Not found bucket_name in config")

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(source)

    if not blob:
        return None

    json_data_string = blob.download_as_string().decode("utf-8")
    return json_data_string


def get_blobs(bucket_name, source) -> list[storage.blob.Blob]:
    try:
        storage_client = storage.Client()
        blobs = storage_client.list_blobs(bucket_name, prefix=source)
    
        return blobs
    except Exception as error:
        print("Access GCS error: ".format(str(error)))

    return []
