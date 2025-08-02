import unittest
from unittest.mock import patch
import os

from common.vcam.client import VCAMClient
from pipelines.funds.vcam_fund_nav_crawler import VcamNAVCrawler


class MutualFundNavCrawlerTest(unittest.TestCase):
    bucket_name: str = "stock_analytics"
    file_path: str = "marketdb/jobs/pythontests/funds"

    def __init__(self, *args, **kwargs):
        super(MutualFundNavCrawlerTest, self).__init__(*args, **kwargs)

        os.environ["BUCKET_NAME"] = self.bucket_name

    def __get_file_path(self, path: str):
        if path.startswith("/"):
            return path
        return f"{self.file_path}/{path}"

    @patch.object(VCAMClient, "_make_get_request")
    @patch.object(VcamNAVCrawler, "do_upload_gcs", return_value=True)
    def test_vcam_nav_crawler_success(self, do_upload_gcs, mock_vcam__make_get_request):
        mock_vcam__make_get_request.return_value = {
            "pagination": {"total": 515, "page": 1, "per_page": 10},
            "data": [
                {
                    "id": 1027,
                    "fund_id": 1,
                    "fund_code": "vcambf",
                    "fund_name": "Quỹ Cân Bằng",
                    "nav": "83724494561.0",
                    "nav_certificate": "14634.56",
                    "posting_date": "01-06-2023",
                    "posting_date_value": 1685577600000,
                },
                {
                    "id": 1025,
                    "fund_id": 1,
                    "fund_code": "vcambf",
                    "fund_name": "Quỹ Cân Bằng",
                    "nav": "104609492734.0",
                    "nav_certificate": "17000.0",
                    "posting_date": "10-03-2023",
                    "posting_date_value": 1678406400000,
                },
            ],
        }

        job = VcamNAVCrawler(api_token="xxx", access_code="yyy")
        input_date = "2023/06/01"
        job.pipeline(input_date=input_date)

        self.assertFalse(job.data_frame.empty)
        self.assertEqual(len(job.data_frame.index), 2)

    @patch.object(VCAMClient, "_make_get_request")
    def test_job_pipeline_no_data(self, mock_vcam__make_get_request):
        mock_vcam__make_get_request.return_value = {"data": []}
        job = VcamNAVCrawler(api_token="xxx", access_code="yyy")
        job.pipeline(input_date="2023/04/07")
        self.assertTrue(job.data_frame.empty)


if __name__ == "__main__":
    unittest.main()
