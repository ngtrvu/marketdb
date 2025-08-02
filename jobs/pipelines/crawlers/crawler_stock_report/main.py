import json
import logging
from datetime import datetime

from pytz import timezone
import pandas as pd
import requests
from time import sleep

from common.tinydwh.datetime_util import get_date_str, VN_TIMEZONE
from common.tinydwh.storage.connector import GCS
from common.tinydwh.storage.utils import get_blobs


class StockReportCrawler:
    parallel = 1
    new_lines = True
    year = 2022

    def __init__(self, bucket_name=None):
        if not bucket_name:
            self.bucket_name = 'stock_analytics'

    def crawl_stock_report_GetBalanceSheet(self, symbol: str, gcs_path: str):
        logging.info(f"Crawling GetBalanceSheet: {symbol}..")

        # GetBalanceSheet
        url = f'https://fiin-fundamental.ssi.com.vn/FinancialStatement/GetBalanceSheet?OrganCode={symbol}'
        report = 'GetBalanceSheet'
        response = requests.get(url)
        items = response.json().get('items', [])
        if len(items) > 0:
            yearly_reports = items[0]['yearly']
            quarterly_reports = items[0]['quarterly']

            file_path = f"{gcs_path}/{symbol}/{report}_yearly.json"
            GCS().upload_to_gcs(
                dict_data=yearly_reports,
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

            file_path = f"{gcs_path}/{symbol}/{report}_quarterly.json"
            GCS().upload_to_gcs(
                dict_data=quarterly_reports,
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

    def crawl_stock_report_GetIncomeStatement(self, symbol: str, gcs_path: str):
        logging.info(f"Crawling GetIncomeStatement: {symbol}..")

        # GetBalanceSheet
        url = f'https://fiin-fundamental.ssi.com.vn/FinancialStatement/GetIncomeStatement?OrganCode={symbol}'
        report = 'GetIncomeStatement'
        response = requests.get(url)
        items = response.json().get('items', [])
        if len(items) > 0:
            yearly_reports = items[0]['yearly']
            quarterly_reports = items[0]['quarterly']

            file_path = f"{gcs_path}/{symbol}/{report}_yearly.json"
            GCS().upload_to_gcs(
                dict_data=yearly_reports,
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

            file_path = f"{gcs_path}/{symbol}/{report}_quarterly.json"
            GCS().upload_to_gcs(
                dict_data=quarterly_reports,
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

    def crawl_stock_report_GetCashFlow(self, symbol: str, gcs_path: str):
        logging.info(f"Crawling GetCashFlow: {symbol}..")

        # GetBalanceSheet
        url = f'https://fiin-fundamental.ssi.com.vn/FinancialStatement/GetCashFlow?OrganCode={symbol}'
        report = 'GetCashFlow'
        response = requests.get(url)
        items = response.json().get('items', [])
        if len(items) > 0:
            yearly_reports = items[0]['yearly']
            quarterly_reports = items[0]['quarterly']

            file_path = f"{gcs_path}/{symbol}/{report}_yearly.json"
            GCS().upload_to_gcs(
                dict_data=yearly_reports,
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

            file_path = f"{gcs_path}/{symbol}/{report}_quarterly.json"
            GCS().upload_to_gcs(
                dict_data=quarterly_reports,
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

    def crawl_stock_report_GetFinancialRatio(self, symbol: str, gcs_path: str):
        logging.info(f"Crawling GetFinancialRatioV2: {symbol}..")

        # GetFinancialRatioV2 - Quarterly
        url = f'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/GetFinancialRatioV2?Type=Company&OrganCode={symbol}&Timeline={self.year}_4&Timeline={self.year}_3&Timeline={self.year}_2&Timeline={self.year}_1'
        report = 'GetFinancialRatio'
        response = requests.get(url)
        items = response.json().get('items', [])
        if len(items) > 0:
            quarterly_reports = []
            for item in items:
                quarterly_reports.append(item['value'])

            file_path = f"{gcs_path}/{symbol}/{report}_quarterly.json"
            GCS().upload_to_gcs(
                dict_data=quarterly_reports,
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

        # GetFinancialRatioV2 - Yearly
        url = f'https://fiin-fundamental.ssi.com.vn/FinancialAnalysis/GetFinancialRatioV2?Type=Company&OrganCode={symbol}&Timeline=2022_5&Timeline=2021_5&Timeline=2020_5&Timeline=2019_5&Timeline=2018_5'
        report = 'GetFinancialRatio'
        response = requests.get(url)
        items = response.json().get('items', [])
        if len(items) > 0:
            yearly_reports = []
            for item in items:
                yearly_reports.append(item['value'])

            file_path = f"{gcs_path}/{symbol}/{report}_yearly.json"
            GCS().upload_to_gcs(
                dict_data=yearly_reports,
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

    def crawl_stock_report_CashDividendAnalysis(self, symbol: str, gcs_path: str):
        logging.info(f"Crawling CashDividendAnalysis: {symbol}..")

        # GetAnalysis - All years
        url = f'https://fiin-fundamental.ssi.com.vn/CashDividendAnalysis/GetAnalysis?language=vi&OrganCode={symbol}&Code={symbol}'
        report = 'CashDividendAnalysis'
        response = requests.get(url)
        items = response.json().get('items', [])
        if len(items) > 0:
            file_path = f"{gcs_path}/{symbol}/{report}.json"
            GCS().upload_to_gcs(
                dict_data=items[0],
                bucket_name="stock_analytics",
                gcs_path=file_path
            )

    def crawl_stock_report(self, symbol: str, gcs_path: str):
        try:
            self.crawl_stock_report_GetBalanceSheet(symbol, gcs_path)
        except Exception as e:
            logging.info(str(e))

        try:
            self.crawl_stock_report_GetIncomeStatement(symbol, gcs_path)
        except Exception as e:
            logging.info(str(e))

        try:
            self.crawl_stock_report_GetCashFlow(symbol, gcs_path)
        except Exception as e:
            logging.info(str(e))

        try:
            self.crawl_stock_report_GetFinancialRatio(symbol, gcs_path)
        except Exception as e:
            logging.info(str(e))

        try:
            self.crawl_stock_report_CashDividendAnalysis(symbol, gcs_path)
        except Exception as e:
            logging.info(str(e))

    def load_symbols(self, input_date) -> list:
        # symbols = ['SSI', 'VCI', 'VND', 'ACB', 'VPB', 'VCB', 'CTG', 'BVH', 'HPG', 'MWG', 'MSN', 'FPT']
        # TODO: load mass stocks
        base_path = f"marketdb/stock/{input_date}/stock.json"
        blobs = get_blobs(bucket_name=self.bucket_name, source=base_path)
        data_frame = pd.DataFrame()
        for blob in blobs:
            try:
                json_str = blob.download_as_string().decode("utf-8")
                df = pd.read_json(json_str, lines=True)
                data_frame = pd.concat([data_frame, df])
            except Exception as error:
                logging.error(f"Get blob error: {error}")

        symbols = data_frame['symbol'].unique().tolist()
        return symbols[0:2]

    def pipeline(self, year=None, input_date=None, symbol=None):
        if not year:
            year = 2022
        self.year = year

        if not input_date:
            # Get default by today
            date_obj = datetime.now(tz=timezone(VN_TIMEZONE))
            input_date = get_date_str(date_obj, date_format="%Y/%m/%d", tz=VN_TIMEZONE)

        gcs_path = f"crawler/stock/stock-reports/{input_date}"

        if not symbol:
            symbols = self.load_symbols(input_date=input_date)
        else:
            symbols = symbol.split(",")
        count = 0
        total = len(symbols)
        for symbol in symbols:
            self.crawl_stock_report(symbol, gcs_path)

            count += 1
            seconds = 1
            logging.info(f"Progress: {(count * 100)/total}%. Waiting for {seconds} seconds for the next crawl...")
            sleep(seconds)

        logging.info('Done!')
