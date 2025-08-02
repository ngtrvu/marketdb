import logging
import requests

from common.tinydwh.base import MiniJobBase


class APILoader(MiniJobBase):

    def __init__(self):
        self.data: dict = {}
        self.parallel: int = 10

    def load(self, url: str):
        logging.info(f"Loading data from url {url}")

        res = requests.get(url)
        data = res.json()
        if not data:
            logging.error(f"Cannot get data from {url}, data is null")
            return
        return data

    def pipeline(self, input_date: str = ""):
        raise NotImplementedError()
