import io
import json
import random
import time
import urllib
import urllib3
import requests
from datetime import datetime, timedelta
from pytz import timezone
from fake_headers import Headers
import pandas as pd
from pandas import read_csv

from utils.logger import logger as logging
from common.tinydwh.storage.connector import GCS
from pipelines.crawlers.crawler_mutual_funds_nav.config import (
    ALL_SYMBOLS,
    MutualFundSource,
    DRAGON_CAPITAL_SYMBOLS,
    VINA_CAPITAL_SYMBOLS,
    SSI_SYMBOLS,
    VN_DIRECT_SYMBOLS,
    VIET_CAPITAL_SYMBOLS,
    MIRAE_ASSET_SYMBOLS,
    VIETCOMBANK_SYMBOLS,
    MutualFundNav,
)
from pipelines.crawlers.crawler_mutual_funds_nav.utils import (
    to_dict_price,
    get_source_from_symbol,
)
from pipelines.crawlers.crawler_mutual_funds_nav.fmarket import FMarketCrawler


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_vndaf_currency(str_value: str) -> float:
    if "." not in str_value and "," in str_value:
        vals = str_value.split(",")
        floating_val = vals[-1]
        int_val = "".join(
            [i for i in vals if vals.index(i) != vals.index(floating_val)]
        )
        return float(f"{int_val}.{floating_val}")
    if "." in str_value and "," in str_value:
        dot_seen_first = False
        for c in str_value:
            if c == ".":
                dot_seen_first = True
                break
            if c == ",":
                dot_seen_first = False
                break

        if dot_seen_first:
            return float(str_value.replace(".", "").replace(",", "."))
        else:
            return float(str_value.replace(",", "").replace(".", "."))

    return float(str_value.replace(".", "").replace(",", "."))


def get_latest_nav_url(symbol: str) -> (MutualFundSource, str):
    source = get_source_from_symbol(symbol)
    latest_url = None
    to_date = datetime.now()

    if source == MutualFundSource.DRAGON_CAPITAL and symbol in DRAGON_CAPITAL_SYMBOLS:
        latest_url = f"https://api.dragoncapital.com.vn/nav/getLatestValue.php?trade_code={symbol}"
    elif source == MutualFundSource.VINA_CAPITAL and symbol in VINA_CAPITAL_SYMBOLS:
        year = to_date.year
        latest_url = f"https://apis.mio.vinacapital.com/web/v1/api/wm/fund/performance-load?productCode={symbol}&year={year}"
    elif source == MutualFundSource.SSI and symbol in SSI_SYMBOLS:
        # set 30 days ~ 1 month to make our request looklike normal user
        from_date = to_date - timedelta(days=30)
        date_started = urllib.parse.quote_plus(from_date.strftime("%d/%m/%Y"))
        date_ended = urllib.parse.quote_plus(to_date.strftime("%d/%m/%Y"))
        page_id = None
        if symbol in ["SSI-SCA", "SSISCA"]:
            page_id = 17
        elif symbol in ["SSIBF"]:
            page_id = 15
        elif symbol in ["VLGF"]:
            page_id = 73
        if page_id:
            latest_url = f"https://ssi.com.vn/ssiam/hieu-qua-dau-tu-quy/compare-chart?page_id={page_id}&page_compare_id=vn_index&date_started={date_started}&date_ended={date_ended}"
    elif source == MutualFundSource.VN_DIRECT and symbol in VN_DIRECT_SYMBOLS:
        latest_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSSuhuAEtnIlPQpbsfEkeZoZaxsPX_3t-vFQ9QN_pweOsAaY05uB1h1cTxOfND448ElWckApBY7zyEE/pub?gid=0&single=true&output=csv"
    elif source == MutualFundSource.VIET_CAPITAL and symbol in VIET_CAPITAL_SYMBOLS:
        latest_url = f"https://vietcapital.com.vn/performance_chart?locale=vi&fund_code={symbol.lower()}"
    # elif source == MutualFundSource.STAG_VCAM and symbol in VIET_CAPITAL_SYMBOLS:
    #     latest_url = f"https://api.fmarket.vn/home/product/{symbol}"
    elif source == MutualFundSource.MIRAE_ASSET and symbol in MIRAE_ASSET_SYMBOLS:
        latest_url = f"https://api.fmarket.vn/home/product/{symbol}"
    elif source == MutualFundSource.VIETCOMBANK and symbol in VIETCOMBANK_SYMBOLS:
        custom_symbol_vietcombank = symbol.replace("-", "")
        latest_url = f"https://api.fmarket.vn/home/product/{custom_symbol_vietcombank}"

    return source, latest_url


def crawl_latest_fund_nav(symbol: str):
    source, latest_url = get_latest_nav_url(symbol)
    daily_nav = None
    if not latest_url:
        return None

    headers = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate only Windows platform
        headers=True,  # generate misc headers
    )

    logging.info(f"access {latest_url}")
    headers = headers.generate()

    try:
        res = requests.get(latest_url, headers=headers, timeout=10)
        res.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {symbol}: {e}")
        return None

    if res.status_code == 200:
        if source == MutualFundSource.DRAGON_CAPITAL:
            latest_nav = res.json()
            daily_nav = MutualFundNav(
                symbol=symbol,
                nav=float(latest_nav.get("nav_ccq")),
                nav_date_str=latest_nav.get("nav_date"),
            )
        elif source == MutualFundSource.VINA_CAPITAL:
            latest_nav = res.json()
            daily_nav = MutualFundNav(
                symbol=symbol,
                nav=float(latest_nav.get("data").get("nav")),
                nav_date_str=latest_nav.get("data").get("navDate"),
            )
        elif source == MutualFundSource.SSI:
            latest_nav = res.json()
            chart_data = latest_nav.get("chartData").get("data")
            # sort by timestamp
            sorted_chart_data = sorted(chart_data, key=lambda tup: tup[0])
            daily_nav = MutualFundNav(
                symbol=symbol,
                nav=sorted_chart_data[-1][1],
                nav_date_str=datetime.fromtimestamp(
                    sorted_chart_data[-1][0] / 1000
                ).strftime("%Y-%m-%d"),
            )
        elif source == MutualFundSource.VN_DIRECT:
            chart_df = read_csv(latest_url)
            chart_df = chart_df[["Ngày", symbol]]
            chart_df = chart_df[~chart_df[symbol].isnull()]
            # chart_df = chart_df.tail(30)
            # logging.info(chart_df.tail())
            chart_df["nav_date"] = pd.to_datetime(chart_df["Ngày"], format="%d/%m/%Y")
            chart_df["nav_date"] = chart_df["nav_date"].dt.strftime("%Y-%m-%d")
            chart_df = chart_df.sort_values(by="nav_date")

            daily_nav = MutualFundNav(
                symbol=symbol,
                nav=parse_vndaf_currency(chart_df[symbol].iloc[-1]),
                nav_date_str=chart_df["nav_date"].iloc[-1],
            )

        elif source == MutualFundSource.VIET_CAPITAL:
            try:
                dfs = pd.read_html(io.StringIO(res.text))
            except ValueError as e:
                logging.error(
                    f"[VCAM] Failed status {res.status_code} to crawl {symbol} caused by {e}"
                )
                dfs = []

            if len(dfs) < 1:
                return None
            latest_nav = dfs[0]
            latest_nav["nav_date"] = pd.to_datetime(
                latest_nav["Ngày"], format="%d-%m-%Y"
            )
            latest_nav["nav_date"] = latest_nav["nav_date"].dt.strftime("%Y-%m-%d")
            latest_nav["NAV/1 CCQ (VNĐ)"] = latest_nav["NAV/1 CCQ (VNĐ)"].apply(float)
            daily_nav = MutualFundNav(
                symbol=symbol,
                nav=latest_nav["NAV/1 CCQ (VNĐ)"].iloc[0],
                nav_date_str=latest_nav["nav_date"].iloc[0],
            )
        elif source == MutualFundSource.STAG_VCAM:
            latest_nav = res.json()
            item = latest_nav.get("data", {})
            if item.get("code", "").lower() == symbol.lower():
                # tradingSession = item.get('tradingSession', {})
                # tradingTime = tradingSession.get('tradingTime', 0)
                extra = item.get("extra")
                trading_time = datetime.fromtimestamp(
                    extra.get("lastNAVDate", pd.Timestamp.now()) / 1000
                ).strftime("%Y-%m-%d")
                nav_date = pd.to_datetime(trading_time)
                nav_date_str = nav_date.strftime("%Y-%m-%d")
                nav = float(item.get("nav", 0))
                if nav > 0:
                    daily_nav = MutualFundNav(
                        symbol=symbol, nav=nav, nav_date_str=nav_date_str
                    )
        elif source == MutualFundSource.MIRAE_ASSET:
            latest_nav = res.json()
            # Parse the HTML content

            item = latest_nav.get("data", {})
            if item.get("code", "").lower() == symbol.lower():
                # tradingSession = item.get('tradingSession', {})
                # tradingTime = tradingSession.get('tradingTime', 0)
                extra = item.get("extra")
                trading_time = datetime.fromtimestamp(
                    extra.get("lastNAVDate", pd.Timestamp.now()) / 1000
                ).strftime("%Y-%m-%d")
                nav_date = pd.to_datetime(trading_time)
                nav_date_str = nav_date.strftime("%Y-%m-%d")
                nav = float(item.get("nav", 0))
                if nav > 0:
                    daily_nav = MutualFundNav(
                        symbol=symbol, nav=nav, nav_date_str=nav_date_str
                    )

        elif source == MutualFundSource.VIETCOMBANK:
            latest_nav = res.json()
            # Parse the HTML content

            item = latest_nav.get("data", {})
            if item.get("shortName", "").lower() == symbol.lower():
                extra = item.get("extra")
                trading_time = datetime.fromtimestamp(
                    extra.get("lastNAVDate", pd.Timestamp.now()) / 1000,
                    tz=timezone("Asia/Ho_Chi_Minh"),
                ).strftime("%Y-%m-%d")
                nav_date = pd.to_datetime(trading_time)
                nav_date_str = nav_date.strftime("%Y-%m-%d")
                nav = float(item.get("nav", 0))
                if nav > 0:
                    daily_nav = MutualFundNav(
                        symbol=symbol, nav=nav, nav_date_str=nav_date_str
                    )

    logging.info(f"Crawled NAV {symbol}: {daily_nav}, date: {daily_nav.nav_date_str}")
    return daily_nav


def mutual_funds_nav_daily_main(
    symbol: str,
    base_path: str,
    bucket_name: str = "stock_analytics",
    gcs_date: str = None,
):
    try:
        fund_nav = crawl_latest_fund_nav(symbol=symbol)
    except Exception as e:
        logging.error(f"Failed to crawl {symbol} caused by {e}")
        return {}

    if not fund_nav or not fund_nav.nav_date_str:
        logging.error(f"Failed to crawl {symbol} caused by {fund_nav}")
        return {}

    nav_json = json.dumps(to_dict_price(fund_nav), indent=4)

    filename = f"fund_nav_{symbol}.json"
    if not gcs_date:
        gcs_date = fund_nav.nav_datetime.strftime("%Y/%m/%d")

    gcs = GCS()

    gcs_path = f"{base_path}/{gcs_date}/{filename}"
    logging.info(f"Uploading to GCS: {gcs_path}")
    gcs.upload_dict(dict_json=nav_json, bucket_name=bucket_name, gcs_path=gcs_path)

    current_gcs_date = datetime.now().strftime("%Y/%m/%d")
    gcs_path = f"{base_path}/{current_gcs_date}/{filename}"
    logging.info(f"Uploading to GCS: {gcs_path}")
    gcs.upload_dict(dict_json=nav_json, bucket_name=bucket_name, gcs_path=gcs_path)

    return nav_json


def mutual_funds_nav_history_main(
    symbol: str,
    bucket_name: str = "stock_analytics",
    base_path: str = "crawler/mutual_fund_nav_history",
    start_date: str = None,
    end_date: str = None,
):
    crawler = FMarketCrawler(
        fund_code=symbol,
        bucket_name=bucket_name,
        start_date=start_date,
        end_date=end_date,
    )

    # Export NAV history to JSON
    df = crawler.load_nav_history_to_gcs(base_path=base_path)
    logging.info(f"Fetched {symbol}: {len(df)} rows")
    return True
