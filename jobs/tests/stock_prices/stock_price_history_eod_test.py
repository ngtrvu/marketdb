import unittest
from unittest.mock import patch

from common.tinydwh.datetime_util import get_previous_date_str
from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.stock_prices.stock_price_history_eod import (
    StockPriceHistoryEOD,
)


class StockPriceHistoryEODTest(GcsTestCase):
    file_path: str = "marketdb/jobs/pythontests/stock_prices"
    bucket_name: str = "stock_analytics"

    def get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_job_pipeline_no_data(self, check_calendar):
        check_calendar.return_value = True
        job = StockPriceHistoryEOD()
        job.pipeline(input_date="2345/01/01")

        self.assertTrue(job.data_frame.empty)

    @patch(
        "pipelines.stock_prices.stock_price_history_eod.StockPriceHistoryEOD"
        ".get_previous_trading_date_str"
    )
    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_stock_price_history_eod_success_with_adjustment(
        self, check_calendar, get_previous_trading_date_str
    ):
        input_date = "2023/12/05"
        input_date_path = str.replace(input_date, "/", "_")
        check_calendar.return_value = True
        get_previous_trading_date_str.return_value = get_previous_date_str(
            input_date, n_day=1
        )
        previous_trading_date = get_previous_trading_date_str.return_value
        previous_trading_date_path = previous_trading_date.replace("/", "_")

        # get the daily stock prices on input_date
        blob = self.bucket.blob(
            f"marketdb/stock_price_intraday/{input_date}/stock_price_ohlc.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{input_date_path}_intraday_price_ohlc.json"
        )
        blob.upload_from_filename(file_path)

        # get stock coporate actions on input_date
        blob = self.bucket.blob(
            f"marketdb/corporate_action/{input_date}/corporate_action.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{input_date_path}_corporate_action.json"
        )
        blob.upload_from_filename(file_path)

        # get the bulk OHLC stock prices on previous trading date
        blob = self.bucket.blob(
            f"marketdb/stock_price_ohlc_bulk_v3/{previous_trading_date}/stock_price_bulk.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{previous_trading_date_path}_stock_price_bulk.json"
        )
        blob.upload_from_filename(file_path)

        # run job at the end of the day
        job = StockPriceHistoryEOD()
        job.pipeline(input_date=input_date)
        bulk_stock_price_CMG = job.data_frame.query("symbol=='CMG'")

        self.assertFalse(job.data_frame.empty)
        self.assertTupleEqual(job.data_frame.shape, (40, 15))
        self.assertEqual(bulk_stock_price_CMG.iloc[0]["close"], 38250)
        self.assertEqual(bulk_stock_price_CMG.iloc[1]["close"], 37876)
        self.assertEqual(bulk_stock_price_CMG.iloc[2]["close"], 38189)

    @patch(
        "pipelines.stock_prices.stock_price_history_eod.StockPriceHistoryEOD"
        ".get_previous_trading_date_str"
    )
    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_stock_price_history_eod_success_duplicated_cash_events_with_adjustment(
        self, check_calendar, get_previous_trading_date_str
    ):
        input_date = "2023/11/20"
        input_date_path = str.replace(input_date, "/", "_")
        check_calendar.return_value = True
        get_previous_trading_date_str.return_value = "2023/11/17"
        previous_trading_date = get_previous_trading_date_str.return_value
        previous_trading_date_path = previous_trading_date.replace("/", "_")

        # get the daily stock prices on input_date
        blob = self.bucket.blob(
            f"marketdb/stock_price_intraday/{input_date}/stock_price_ohlc.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{input_date_path}_intraday_price_ohlc.json"
        )
        blob.upload_from_filename(file_path)

        # get stock coporate actions on input_date
        blob = self.bucket.blob(
            f"marketdb/corporate_action/{input_date}/corporate_action.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{input_date_path}_corporate_action.json"
        )
        blob.upload_from_filename(file_path)

        # get the bulk OHLC stock prices on previous trading date
        blob = self.bucket.blob(
            f"marketdb/stock_price_ohlc_bulk_v3/{previous_trading_date}/stock_price_bulk.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{previous_trading_date_path}_stock_price_bulk.json"
        )
        blob.upload_from_filename(file_path)

        # run job at the end of the day
        job = StockPriceHistoryEOD()
        job.pipeline(input_date=input_date)

        self.assertFalse(job.data_frame.empty)
        self.assertTupleEqual(job.data_frame.shape, (20, 15))

        bulk_stock_price_CMG = job.data_frame.query("symbol=='CMG'")
        self.assertEqual(bulk_stock_price_CMG.iloc[0]["close"], 47300)
        self.assertEqual(bulk_stock_price_CMG.iloc[1]["close"], 47450)
        self.assertEqual(bulk_stock_price_CMG.iloc[2]["close"], 47500)

        bulk_stock_price_MAC = job.data_frame.query("symbol=='MAC'")
        self.assertEqual(bulk_stock_price_MAC.iloc[0]["close"], 10400)
        self.assertEqual(bulk_stock_price_MAC.iloc[1]["close"], 10000)
        self.assertEqual(bulk_stock_price_MAC.iloc[2]["close"], 9905)

    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_stock_price_history_eod_empty_input(self, check_calendar):
        check_calendar.return_value = True
        input_date = "2023/12/08"

        # get the daily stock prices on input_date
        blob = self.bucket.blob(f"marketdb/stock_price_intraday/{input_date}/xyz.json")
        file_path = self.get_file_path(
            "files/stock_price_ohlc_bulk_v2/2023_12_05_intraday_price_ohlc.json"
        )
        blob.upload_from_filename(file_path)

        # get stock coporate actions on input_date
        blob = self.bucket.blob(
            f"marketdb/corporate_action/{input_date}/corporate_action.json"
        )
        file_path = self.get_file_path(
            "files/stock_price_ohlc_bulk_v2/2023_12_05_corporate_action.json"
        )
        blob.upload_from_filename(file_path)

        # get the bulk stock prices on previous trading date
        blob = self.bucket.blob(
            f"marketdb/stock_price_ohlc_bulk_v3/2023/12/07/stock_price_bulk.json"
        )
        file_path = self.get_file_path(
            "files/stock_price_ohlc_bulk_v2/2023_12_04_stock_price_bulk.json"
        )
        blob.upload_from_filename(file_path)

        # run job at the end of the day
        job = StockPriceHistoryEOD()
        job.pipeline(input_date=input_date)

        self.assertTrue(job.data_frame.empty)

    @patch(
        "pipelines.stock_prices.stock_price_history_eod.StockPriceHistoryEOD"
        ".get_previous_trading_date_str"
    )
    @patch(
        "common.mdb.client.MarketdbClient.check_calendar"
    )
    def test_stock_price_history_eod_success_with_no_corporate_actions(
        self, check_calendar, get_previous_trading_date_str
    ):
        input_date = "2023/11/20"
        input_date_path = str.replace(input_date, "/", "_")
        check_calendar.return_value = True
        get_previous_trading_date_str.return_value = "2023/11/17"
        previous_trading_date = get_previous_trading_date_str.return_value
        previous_trading_date_path = previous_trading_date.replace("/", "_")

        # get the daily stock prices on input_date
        blob = self.bucket.blob(
            f"marketdb/stock_price_intraday/{input_date}/stock_price_ohlc.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{input_date_path}_intraday_price_ohlc.json"
        )
        blob.upload_from_filename(file_path)

        # get stock coporate actions on input_date
        blob = self.bucket.blob(
            f"marketdb/corporate_action/{input_date}/corporate_action.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{input_date_path}_corporate_action_empty.json"
        )
        blob.upload_from_filename(file_path)

        # get the bulk OHLC stock prices on previous trading date
        blob = self.bucket.blob(
            f"marketdb/stock_price_ohlc_bulk_v3/{previous_trading_date}/stock_price_bulk.json"
        )
        file_path = self.get_file_path(
            f"files/stock_price_ohlc_bulk_v2/{previous_trading_date_path}_stock_price_bulk.json"
        )
        blob.upload_from_filename(file_path)

        # run job at the end of the day
        job = StockPriceHistoryEOD()
        job.pipeline(input_date=input_date)

        self.assertFalse(job.data_frame.empty)
        self.assertTupleEqual(job.data_frame.shape, (20, 15))

        bulk_stock_price_CMG = job.data_frame.query("symbol=='CMG'")
        self.assertEqual(bulk_stock_price_CMG.iloc[0]["close"], 47300)
        self.assertEqual(bulk_stock_price_CMG.iloc[1]["close"], 47450)
        self.assertEqual(bulk_stock_price_CMG.iloc[2]["close"], 47500)

        bulk_stock_price_MAC = job.data_frame.query("symbol=='MAC'")
        self.assertEqual(bulk_stock_price_MAC.iloc[0]["close"], 10400)
        self.assertEqual(bulk_stock_price_MAC.iloc[1]["close"], 10500)
        self.assertEqual(bulk_stock_price_MAC.iloc[2]["close"], 10400)


if __name__ == "__main__":
    unittest.main()
