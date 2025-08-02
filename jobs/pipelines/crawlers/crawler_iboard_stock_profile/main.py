import http.client
import json
import logging
from time import sleep

import requests
from fake_headers import Headers

from common.tinydwh.datetime_util import VN_TIMEZONE, get_date_str
from common.tinydwh.storage.connector import GCS
from common.mdb.client import MarketdbClient


class IBoardStockProfileCrawler:
    parallel = 1

    def __init__(self):
        pass

    def pipeline(self, input_date=None, backfill=False):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        self.crawl_stocks(input_date, backfill)
        self.crawl_etfs(input_date, backfill)

    def crawl(self, symbol: str):
        payload = json.dumps(
            {
                "operationName": "companyProfile",
                "variables": {"symbol": f"{symbol}", "language": "vn"},
                "query": """
                query companyProfile($symbol: String!, $language: String) {\n  
                    companyProfile(symbol: $symbol, language: $language) {\n    
                        symbol\n    subsectorcode\n    industryname\n    supersector\n    sector\n    subsector\n    
                        foundingdate\n    chartercapital\n    numberofemployee\n    banknumberofbranch\n    
                        companyprofile\n    listingdate\n    exchange\n    firstprice\n    issueshare\n    
                        listedvalue\n    companyname\n    __typename\n  
                    }\n  
                    companyStatistics(symbol: $symbol) {\n    symbol\n    ttmtype\n    marketcap\n    
                        sharesoutstanding\n    bv\n    beta\n    eps\n    dilutedeps\n    pe\n    pb\n    
                        dividendyield\n    totalrevenue\n    profit\n    asset\n    roe\n    roa\n    npl\n    
                        financialleverage\n    __typename\n  
                    }\n}\n
            """,
            }
        )

        grahpql_ssi_host = "finfo-iboard.ssi.com.vn"
        logging.debug("Crawling %s" % grahpql_ssi_host)

        headers = Headers(
            browser="chrome",
            headers=True,
        )
        headers = headers.generate()
        headers["Content-Type"] = "application/json"

        conn = http.client.HTTPSConnection(grahpql_ssi_host)
        conn.request("POST", "/graphql", payload, headers)
        res = conn.getresponse()
        status_code = res.getcode()

        if status_code == 200:
            try:
                response_data = res.read()
                response_json = json.loads(response_data)
                return response_json.get("data", {})
            except Exception as ex:
                logging.error(f"Error: {ex}")
        else:
            logging.error(f"Crawled error - status code: {status_code} {res}")

    def crawl_profile(self, symbol: str, gcs_path: str):
        logging.debug(f"Crawling {symbol}..")
        data = self.crawl(symbol=symbol)

        if data and data != {}:
            file_path = f"{gcs_path}/{symbol}.json"
            logging.info(f"Uploading {symbol} to gcs: {file_path}..")
            GCS().upload_to_gcs(dict_data=data, bucket_name="stock_analytics", gcs_path=file_path)
        else:
            logging.error("Invalid crawled data")

    def load_stock_symbols(self):
        # load new daily listed
        symbols = MarketdbClient().get_stock_symbols(status=1001)

        # url = "/v1/stocks?outstanding_shares=0"
        # symbols = MarketdbClient().get_stock_symbols(outstanding_shares=0)

        # TODO: load new stock events

        return symbols

    def load_etf_symbols(self):
        # load new daily listed
        symbols = MarketdbClient().get_etf_symbols(status=1001)
        return symbols

    def crawl_etfs(self, input_date: str, backfill: bool = False):
        gcs_path = f"crawler/iboard_etf_profile/{input_date}"

        if backfill:
            logging.info(f"Backfill for all etfs...")
            symbols = MarketdbClient().get_etf_symbols()
        else:
            symbols = self.load_etf_symbols()

        count = 1
        total = len(symbols)
        for symbol in symbols:
            self.crawl_profile(symbol, gcs_path)

            count += 1
            seconds = 1.5
            logging.info(
                f"Progress: {(count * 100)/total}%. Waiting for {seconds} seconds for the next crawl..."
            )
            sleep(seconds)

        logging.info("Done!")

    def crawl_stocks(self, input_date: str, backfill: bool = False):
        gcs_path = f"crawler/iboard_stock_profile/{input_date}"

        if backfill:
            logging.info(f"Backfill for all stocks...")
            symbols = MarketdbClient().get_stock_symbols()
        else:
            symbols = self.load_stock_symbols()

        count = 1
        total = len(symbols)
        for symbol in symbols:
            self.crawl_profile(symbol, gcs_path)

            count += 1
            seconds = 1.5
            logging.info(
                f"Progress: {(count * 100)/total}%. Waiting for {seconds} seconds for the next crawl..."
            )
            sleep(seconds)

        logging.info("Done!")
