import os
import unittest
from unittest.mock import patch

import pandas as pd

from common.tinydwh.storage.test_utils import GcsTestCase
from pipelines.funds.mutual_fund_nav_analytics_etl import (
    MutualFundNAVAnalyticsETL,
)


class MutualFundNavAnalyticsTest(GcsTestCase, unittest.TestCase):
    file_path: str = "marketdb/jobs/pythontests/funds"
    bucket_name: str = "gcs-test-bucket"

    def __init__(self, *args, **kwargs):
        super(MutualFundNavAnalyticsTest, self).__init__(*args, **kwargs)

        os.environ["BUCKET_NAME"] = self.bucket_name

    def setUp(self):
        super().setUp(self.bucket_name)

    def __get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch.object(MutualFundNAVAnalyticsETL, "do_indexing_v2")
    @patch.object(MutualFundNAVAnalyticsETL, "do_indexing")
    @patch.object(MutualFundNAVAnalyticsETL, "load")
    def test_vcam_nav_analytics_success(
        self, mock_load_gcs, mock_do_indexing, mock_do_indexing_v2
    ):
        data = [
            {
                "id": 14730,
                "created": "2023-07-26T08:59:20.243088+00:00",
                "modified": 1690364476815,
                "symbol": "VCAMBF",
                "date": "2018-01-31",
                "datetime": "2018-01-31T17:00:00+00:00",
                "nav": 8754.48,
            },
            {
                "id": 14740,
                "created": "2023-07-26T08:59:20.243088+00:00",
                "modified": 1690364476815,
                "symbol": "VCAMBF",
                "date": "2019-01-31",
                "datetime": "2019-01-31T17:00:00+00:00",
                "nav": 9754.48,
            },
            {
                "id": 14744,
                "created": "2023-07-26T08:59:20.243088+00:00",
                "modified": 1690364476815,
                "symbol": "VCAMBF",
                "date": "2020-07-31",
                "datetime": "2020-07-30T17:00:00+00:00",
                "nav": 10754.48,
            },
            {
                "id": 14745,
                "created": "2023-07-26T08:59:20.251231+00:00",
                "modified": 1690364476823,
                "symbol": "VCAMBF",
                "date": "2020-08-06",
                "datetime": "2020-08-05T17:00:00+00:00",
                "nav": 11046.77,
            },
            {
                "id": 14869,
                "created": "2023-07-26T08:59:21.321889+00:00",
                "modified": 1690364477722,
                "symbol": "VCAMBF",
                "date": "2022-08-04",
                "datetime": "2022-08-03T17:00:00+00:00",
                "nav": 15080.64,
            },
            {
                "id": 15220,
                "created": "2023-08-04T10:05:49.949665+00:00",
                "modified": 1691323801252,
                "symbol": "VCAMBF",
                "date": "2023-08-03",
                "datetime": "2023-08-03T09:00:00+00:00",
                "nav": 16132.54,
            },
            {
                "id": 15189,
                "created": "2023-08-01T12:10:01.324877+00:00",
                "modified": 1691064601470,
                "symbol": "VCAMBF",
                "date": "2023-07-31",
                "datetime": "2023-07-31T09:00:00+00:00",
                "nav": 16268.73,
            },
        ]

        vcambf_df = pd.DataFrame(data)

        mock_load_gcs.return_value = vcambf_df.copy()

        job = MutualFundNAVAnalyticsETL()
        input_date = "2023/08/07"
        job.pipeline(input_date=input_date)

        self.assertFalse(job.data_frame.empty)
        self.assertEqual(len(job.data_frame.index), 7)

        self.assertEqual(len(job.analytics_rows), 1)
        self.assertEqual(job.analytics_rows[0].get("symbol"), "VCAMBF")
        self.assertEqual(job.analytics_rows[0].get("annualized_return_n_year"), 5)
        self.assertEqual(
            round(job.analytics_rows[0].get("annualized_return_percentage"), 2), 13.0
        )

    @patch.object(MutualFundNAVAnalyticsETL, "load")
    def test_job_pipeline_no_data(self, mock_load_gcs):
        mock_load_gcs.return_value = pd.DataFrame()
        job = MutualFundNAVAnalyticsETL()
        input_date = "2023/08/07"
        job.pipeline(input_date=input_date)

        self.assertTrue(job.data_frame.empty)


if __name__ == "__main__":
    unittest.main()
