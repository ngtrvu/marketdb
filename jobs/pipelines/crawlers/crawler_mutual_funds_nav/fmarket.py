import json
from datetime import date, datetime, timezone

import pandas as pd
import requests

from utils.logger import logger as logging
from common.tinydwh.storage.connector import GCS


class FMarketCrawler:
    data: dict

    def __init__(
        self, fund_code, start_date=None, end_date=None, bucket_name="stock_analytics"
    ):
        self.fund_code = fund_code
        self.base_url = "https://api.fmarket.vn/home/product/"
        self.nav_history_url = "https://api.fmarket.vn/res/product/get-nav-history"
        self.data = self.fetch_data()
        self.bucket_name = bucket_name
        self.start_date = start_date
        self.end_date = end_date

    def fetch_data(self):
        url = f"{self.base_url}{self.fund_code}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()["data"]

        logging.error(
            f"Failed to fetch data for symbol {self.fund_code}: HTTP {response.status_code} from url: {url}"
        )
        return None

    def get_fund_id(self):
        if "id" not in self.data:
            return None
        return self.data["id"]

    def get_fund_name(self):
        if "name" not in self.data:
            return None
        return self.data["name"]

    def get_current_nav(self):
        if "nav" not in self.data:
            return None
        return self.data["nav"]

    def get_current_nav_date(self) -> datetime:
        if "extra" not in self.data:
            return pd.Timestamp.now()
        extra = self.data.get("extra")
        return datetime.fromtimestamp(
            extra.get("lastNAVDate", pd.Timestamp.now()) / 1000
        )

    @staticmethod
    def format_utc_timestamp(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S+00:00")

    def get_nav_history_df(
        self, from_date=None, to_date=None, is_all_data=1
    ) -> pd.DataFrame:
        product_id = self.get_fund_id()
        if not product_id:
            return pd.DataFrame()

        payload = {
            "isAllData": is_all_data,
            "productId": product_id,
            "fromDate": from_date,
            "toDate": to_date,
        }

        response = requests.post(self.nav_history_url, json=payload, timeout=10)
        if response.status_code == 200:
            try:
                nav_history = response.json()["data"]
                df = pd.DataFrame(nav_history)

                # Set symbol
                df["symbol"] = self.fund_code
                df["date"] = pd.to_datetime(df["navDate"]).dt.strftime("%Y-%m-%d")

                # Drop duplicates based on symbol and date
                df = df.drop_duplicates(
                    subset=["symbol", "date"], keep="last"
                ).reset_index(drop=True)

                # Format navDate to UTC timestamp string
                df["datetime"] = (
                    pd.to_datetime(df["navDate"])
                    .dt.tz_localize("UTC")
                    .apply(self.format_utc_timestamp)
                )
                # Current time in UTC format
                current_time = self.format_utc_timestamp(datetime.now(timezone.utc))
                df["created"] = current_time
                df["modified"] = current_time

                df = df[["created", "modified", "symbol", "date", "datetime", "nav"]]

                return df
            except Exception as e:
                logging.info(f"Failed to parse NAV history: {e}")
                return pd.DataFrame()

        logging.error(f"Failed to fetch NAV history: HTTP {response.status_code}")
        return pd.DataFrame()

    def get_all_nav_history(self, symbol, bucket_name, base_path):
        from_date = None
        today = date.today()
        to_date = today.strftime("%Y%m%d")
        df = self.get_nav_history_df(from_date, to_date)
        if df.empty:
            return df

        json_records = json.dumps(df.to_dict(orient="records"))
        filename = f"{symbol}_nav_history_upto_{to_date}.json"
        gcs_date = today.strftime("%Y/%m/%d")
        gcs_path = f"{base_path}/{gcs_date}/{filename}"

        # Upload to GCS
        logging.info(f"Uploading to GCS: {gcs_path}")
        gcs = GCS()
        gcs.upload_dict(
            dict_json=json_records, bucket_name=bucket_name, gcs_path=gcs_path
        )
        return df

    def write_to_file(self, file_path, json_records):
        if not file_path:
            logging.info("Sample of NAV history in JSON format:")
            logging.info("\n".join(json_records.split("\n")[:5]))
            return "\n".join(json.dumps(record) for record in json_records)

        with open(file_path, "w", encoding="utf-8") as f:
            for record in json_records:
                json.dump(record, f)
                f.write("\n")
        logging.info(f"NAV history exported to {file_path}")

    def load_nav_history_to_gcs(self, base_path="crawler/mutual_fund_nav_history"):
        logging.info(
            f"ID: {self.get_fund_id()}, Name: {self.get_fund_name()}, NAV: {self.get_current_nav()}"
        )

        # Export NAV history to JSON
        df = self.get_all_nav_history(
            symbol=self.fund_code, bucket_name=self.bucket_name, base_path=base_path
        )
        if self.start_date:
            df = df[df["date"] >= self.start_date]
        if self.end_date:
            df = df[df["date"] <= self.end_date]
        return df
