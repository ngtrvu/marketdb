import os


class Config:
    BUCKET_NAME = os.environ.get("BUCKET_NAME", "stock_analytics")

    def get_bucket_name(self):
        bucket_name = os.environ.get("BUCKET_NAME")
        if not bucket_name:
            raise ValueError("BUCKET_NAME is not set")
        return bucket_name
