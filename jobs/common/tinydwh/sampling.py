import logging
import random
import random

from common.tinydwh.storage.connector import GCS


def random_sampling(data_list: list, min_points=25, max_points=100, ratio=0.2) -> list:
    """
    Sampling from large list to small list and ensure the other of data
    Args:
        data_list (list[any]):
        min_points (int):
        max_points (int):
        ratio (float):

    Returns:

    """
    if not data_list:
        return []

    index_list = range(0, len(data_list))
    if (
        len(index_list) <= min_points
        or len(index_list) < 3
        or len(index_list) <= max_points
    ):
        return data_list

    # ideas when sampling we must keep the head and tail of list
    head = index_list[0]
    tail = index_list[-1]
    mid = index_list[1:-1]
    n_population = len(mid)
    n_sampling = int(len(mid) * ratio)

    # if n_sampling <= min_points:
    #     n_sampling = min_points
    # elif n_sampling >= max_points:
    #     n_sampling = max_points
    # elif n_sampling >= n_population:
    #     n_sampling = n_population

    random.seed(12345)
    sampling_index = [head] + random.sample(mid, min(n_sampling, len(mid))) + [tail]
    sampling_index = sorted(sampling_index)
    sampling_data = [data_list[i] for i in sampling_index]
    return sampling_data


class GCSSampling:
    gcs = None

    def __init__(self, bucket_name, base_path, ratio):
        self.bucket_name = bucket_name
        self.base_path = base_path
        self.ratio = ratio
        self.gcs = GCS()

        self.file_list = self.gcs.list_files(
            bucket_name=self.bucket_name, gcs_path=self.base_path, max_results=1000
        )

    @property
    def count(self):
        total_items = len(self.file_list)
        sampling_count = int(total_items * self.ratio)
        return 1 if sampling_count <= 0 else sampling_count

    def get_sampling(self):
        if self.count > 0:
            logging.debug(f"Getting samples {self.count}")
            return random.sample(self.file_list, self.count)

        logging.debug(f"Getting full list {len(self.file_list)}")
        return self.file_list

    def get_data_from_path(self, file_path):
        return self.gcs.get_json_data(bucket_name=self.bucket_name, gcs_path=file_path)
