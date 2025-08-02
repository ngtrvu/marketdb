import logging

import pandas as pd
from pandas import DataFrame

from common.tinydwh.base import MiniJobBase
from common.tinydwh.datetime_util import get_date_str
from config import Config
from pipelines.marketdb_importer.industry_indexer import IndustryIndexer


class IndustryETL(MiniJobBase):
    data_frame: DataFrame = pd.DataFrame()
    sampling_ratio: float = 1.0

    def __init__(self, sampling_ratio: float = 1.0):
        self.sampling_ratio = sampling_ratio
        self.custom_dtype = {"subsectorcode": str}

    def pipeline(self, input_date=None):
        if not input_date:
            input_date = get_date_str(date_format="%Y/%m/%d", tz="Asia/Ho_Chi_Minh")

        self.load(
            input_date=input_date,
            bucket_name=Config.BUCKET_NAME,
            base_path="crawler/stock/stock-profile-iboard",
        )
        df = self.data_frame

        df = df[~df.subsectorcode.isnull()]
        df = df[df["subsectorcode"].str.len() >= 4]
        df = df.apply(self.transform_row, axis=1)

        industry_data = self.transform_data_frame(df)

        industry_data = list(industry_data.values())

        if len(industry_data) > 0:
            df = pd.DataFrame(industry_data)
            IndustryIndexer().do_indexing(df)

            logging.info(f"Job is successfully executed")
        else:
            logging.warning("No data")

    def transform_row(self, row: dict) -> dict:
        subsectorcode = row.get("subsectorcode")
        sectorcode = subsectorcode[0:3] + "0"
        supersectorcode = subsectorcode[0:2] + "00"
        industrycode = subsectorcode[0:1] + "000"
        industrycode = "0001" if industrycode == "0000" else industrycode

        return {
            "symbol": row.get("symbol"),
            "subsectorcode": subsectorcode,
            "subsector": row.get("subsector"),
            "subsector_id": int("1{0}".format(subsectorcode)),
            "sectorcode": sectorcode,
            "sector": row.get("sector"),
            "sector_id": int("1{0}".format(sectorcode)),
            "supersectorcode": supersectorcode,
            "supersector": row.get("supersector"),
            "supersector_id": int("1{0}".format(supersectorcode)),
            "industrycode": industrycode,
            "industry": row.get("industryname"),
            "industry_id": int("1{0}".format(industrycode)),
        }

    def transform_data_frame(self, df: DataFrame):
        industry_data = {}

        for row in df.tolist():
            # Industry - level 1
            industry_id = row.get("industry_id")

            industry_data[industry_id] = {
                "id": industry_id,
                "name": row.get("industry"),
                "level": 1,
                "icb_code": row.get("industrycode"),
            }

            # Super sector - level 2
            supersector_id = row.get("supersector_id")
            industry_data[supersector_id] = {
                "id": supersector_id,
                "name": row.get("supersector"),
                "level": 2,
                "icb_code": row.get("supersectorcode"),
                "parent_id": industry_id,
            }

            # Sector - level 3
            sector_id = row.get("sector_id")
            industry_data[sector_id] = {
                "id": sector_id,
                "name": row.get("sector"),
                "level": 3,
                "icb_code": row.get("sectorcode"),
                "parent_id": supersector_id,
            }

            # SubSector - level 4
            subsector_id = row.get("subsector_id")
            industry_data[subsector_id] = {
                "id": subsector_id,
                "name": row.get("subsector"),
                "level": 4,
                "icb_code": row.get("subsectorcode"),
                "parent_id": sector_id,
            }

        return industry_data
