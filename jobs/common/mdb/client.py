import json
import os
import requests

from datetime import datetime, time
from django.core.serializers.json import DjangoJSONEncoder

from common.tinydwh.data import sub_dict
from common.tinydwh.datetime_util import (
    VN_TIMEZONE,
    check_time_in_range,
    ensure_tzaware_datetime,
    get_date_str,
    get_datetime_now,
)
from utils.logger import logger

TIMEOUT = 10


class MarketdbClient:

    def __init__(self):
        self.host = os.environ.get("MARKETDB_HOST", "marketdb-api.marketdb:8088")
        self.prefix = os.environ.get("MARKETDB_INTERNAL_PREFIX", "/marketdb-internal/v1")
        self.max_page = os.environ.get("MARKETDB_MAX_PAGE", 100)

    def get(self, api_url: str):
        url = self.__build_marketdb_url(api_url)
        responses = requests.get(url, timeout=TIMEOUT)
        if responses.status_code == 200:
            return responses.json()
        return None

    def post(self, api_url: str, data: dict, headers: dict = None):
        if not headers:
            headers = {"Content-Type": "application/json"}

        url = self.__build_marketdb_url(api_url)
        payload = json.dumps(data, cls=DjangoJSONEncoder)
        responses = requests.post(
            url=url, data=payload, headers=headers, timeout=TIMEOUT
        )

        if responses.status_code == 200 or responses.status_code == 201:
            return True, responses.json()

        if responses.status_code >= 500:
            return False, f"{responses.status_code} Internal server error: {url}"

        if responses.status_code == 404:
            return False, f"404 Not Found: {url}"

        if responses.status_code >= 400:
            truncated_payload = payload[:500] if payload else ""
            resp = responses.text[:500] if responses.text else ""
            message = f"{responses.status_code} Invalid payload: {url} {resp} {truncated_payload}"
            return False, message

        return False, f"{responses.status_code} Something went wrong: {url}"

    def __build_marketdb_url(self, path: str):
        return f"http://{self.host}{self.prefix}{path}"

    def get_stock_prices(self, symbols) -> list:
        result = []
        symbols_string = ",".join(symbols)
        api_path = f"/stock-price-realtimes?symbol__in={symbols_string}"

        json_data = self.get(api_url=api_path)
        if json_data:
            try:
                items = json_data
                if len(items) == 0:
                    return []

                for item in items:
                    price = item.get("price")
                    reference = item.get("reference")
                    change_percentage = item.get("change_percentage_1d")
                    if price and price > 0 and reference and reference > 0:
                        change_percentage = (price - reference) * 100 / reference

                    result.append(
                        {
                            "symbol": item.get("symbol"),
                            "price": price,
                            "change_percentage": change_percentage,
                            "reference": reference,
                            "volume": item.get("volume"),
                            "open": item.get("open"),
                            "high": item.get("high"),
                            "low": item.get("low"),
                            "floor": item.get("floor"),
                            "ceiling": item.get("ceiling"),
                            "type": item.get("type"),
                            "exchange": item.get("exchange"),
                        }
                    )

            except Exception as ex:
                logger.error(f"Call market db failed {ex}")

        return result

    def get_stock_items(self, key_fields: list = None) -> list[dict]:
        items = self.get(api_url="/stocks")

        if not key_fields:
            return items

        result = []
        if items and len(items) > 0:
            for item in items:
                selected_field_items = sub_dict(key_fields, item)
                if selected_field_items:
                    result.append(selected_field_items)

        return result

    def get_stock_symbols(self, status: int = None) -> list:
        symbols = []

        if status:
            items = self.get_stock_items(["symbol", "status"])
            for item in items:
                symbol = item.get("symbol")
                if symbol and item.get("status") == status:
                    symbols.append(symbol)
        else:
            items = self.get_stock_items(["symbol"])
            for item in items:
                symbol = item.get("symbol")
                if symbol:
                    symbols.append(symbol)

        return symbols

    def get_etf_items(self, key_fields: list = None) -> list[dict]:
        items = self.get(api_url="/etfs")

        if not key_fields:
            return items

        result = []
        if items and len(items) > 0:
            for item in items:
                selected_field_items = sub_dict(key_fields, item)
                if selected_field_items:
                    result.append(selected_field_items)

        return result

    def get_etf_symbols(self, status: int = None) -> list:
        symbols = []

        if status:
            items = self.get_etf_items(["symbol", "status"])
            for item in items:
                symbol = item.get("symbol")
                if symbol and item.get("status") == status:
                    symbols.append(symbol)
        else:
            items = self.get_etf_items(["symbol"])
            for item in items:
                symbol = item.get("symbol")
                if symbol:
                    symbols.append(symbol)

        return symbols

    def get_market_index_items(self, key_fields: list = None) -> list[dict]:
        items = self.get(api_url="/market-indexes")

        if not key_fields:
            return items

        result = []
        if items and len(items) > 0:
            for item in items:
                selected_field_items = sub_dict(key_fields, item)
                if selected_field_items:
                    result.append(selected_field_items)

        return result

    def get_market_index_symbols(self) -> list:
        symbols = []
        items = self.get_market_index_items(["symbol"])

        for item in items:
            symbol = item.get("symbol")
            if symbol:
                symbols.append(symbol)

        return symbols

    def check_calendar(self, datetime_obj: datetime = None) -> bool:
        if not datetime_obj:
            datetime_obj = get_datetime_now(tz=VN_TIMEZONE)

        date_str: str = get_date_str(
            datetime_obj, date_format="%Y-%m-%d", tz=VN_TIMEZONE
        )
        resp_data = self.get(api_url=f"/market-calendar/{date_str}")
        if resp_data:
            is_open_now = resp_data["item"]["status"] == 1001
        else:
            raise Exception("No trading calendar data")

        return is_open_now

    def check_calendar_str(self, date_str: str = None) -> bool:
        if not date_str:
            datetime_obj = get_datetime_now(tz=VN_TIMEZONE)
        else:
            datetime_obj = datetime.strptime(date_str, "%Y/%m/%d")

        return self.check_calendar(datetime_obj=datetime_obj)

    def check_trading_time(self, datetime_obj: datetime = None) -> bool:
        is_trading_day = self.check_calendar(datetime_obj)
        if not is_trading_day:
            return False

        # check if time_now is in the trading time (i.e. from 9am to 3pm)
        time_now = ensure_tzaware_datetime(datetime_obj, tz=VN_TIMEZONE).time()
        return check_time_in_range(
            start=time(9, 0, 0), end=time(15, 0, 0), time_obj=time_now
        )

    def update_or_create(
        self, model_name: str, key_name: str, key_value: str, payload: dict
    ) -> tuple[bool, dict]:
        api_path = "/indexer"
        return self.post(
            api_url=api_path,
            data={
                "key_name": key_name,
                "key_value": key_value,
                "model_name": model_name,
                "payload": json.dumps(payload, cls=DjangoJSONEncoder),
            },
        )

    def index_to_db_bulk(
        self,
        model_name: str,
        key_fields: list[str],
        payload: list[dict],
        batch_size: int = 5000,
    ):
        """Index to db bulk in batch chunks to avoid request timeout. By default, batch size is 5000. If payload is
        larger than batch size, it will be split into smaller chunks.

        :param model_name: str, model name
        :param key_fields: list[str], key fields
        :param payload: list[dict], list of items to index
        :param batch_size: int, batch size

        :return: tuple[bool, dict], success and response
        """
        api_path = "/indexer/bulk"

        if len(payload) > batch_size:
            for i in range(0, len(payload), batch_size):
                logger.debug(
                    f"Index to db bulk in batch chunks: {i} - {i + batch_size}"
                )
                success, response = self.post(
                    api_url=api_path,
                    data={
                        "model_name": model_name,
                        "key_fields": key_fields,
                        "items": payload[i : i + batch_size],
                    },
                )
                if not success:
                    logger.warning(
                        f"Index to db bulk failed in chunks: {i} - {i + batch_size}, response {response}"
                    )
            return True, {"total": len(payload)}

        return self.post(
            api_url=api_path,
            data={
                "model_name": model_name,
                "key_fields": key_fields,
                "items": payload,
            },
        )

    def bulk_update(
        self, model_name: str, values: dict, conditions: dict
    ) -> tuple[bool, dict]:
        api_path = "/indexer/bulk-update"
        return self.post(
            api_url=api_path,
            data={
                "model_name": model_name,
                "values": values,
                "conditions": conditions,
            },
        )

    def reindex_search_index(self) -> bool:
        api_path = "/search-index/reindexing"
        return self.post(api_url=api_path, data={})

    def get_xpider_pages(self) -> list:
        api_path = "/xpider-pages"
        return self.get(api_url=api_path)

    def get_xpider_publishers(self) -> list:
        api_path = "/xpider-publishers"
        return self.get(api_url=api_path)

    def export_table_to_gcs(
        self,
        table_name: str,
        bucket_name: str,
        dataset_name: str,
        input_date: str = "",
        directory_name: str = "",
    ) -> tuple[bool, dict]:
        api_path = "/exporter/table"
        payload = {
            "table_name": table_name,
            "dataset_name": dataset_name,
            "bucket_name": bucket_name,
            "directory_name": directory_name,
            "input_date": input_date,
        }
        logger.debug(
            f"Export table {table_name} to bucket {bucket_name} on {input_date}"
        )
        success, response = self.post(
            api_url=api_path,
            data=payload,
        )
        if not success:
            logger.warning(f"Export table {table_name} failed, {response}")
        return success, response

    def get_intraday_price(self, symbol: str) -> tuple[float, int]:
        api_path = f"/intraday/keys/{symbol}"
        return self.get(api_url=api_path)

    def index_intraday_price(self, symbol: str, price: float, timestamp: int):
        api_path = f"/intraday/keys/{symbol}"
        return self.post(
            api_url=api_path,
            data={
                "symbol": symbol,
                "price": price,
                "timestamp": timestamp,
            },
        )

    def initialize_intraday(self):
        api_path = "/intraday/initialize"
        return self.post(api_url=api_path, data={})

    def delete_stock_events(self, symbols: list, public_dates: list):
        api_path = "/indexer/stock-events/delete"
        return self.post(
            api_url=api_path,
            data={
                "symbols": symbols,
                "public_dates": public_dates,
            },
        )
