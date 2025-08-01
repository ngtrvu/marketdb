import json

from google import api_core
from google.api_core.exceptions import RetryError
from google.cloud import pubsub_v1

from common.utils.logger import logger


class PubSubGcp:
    topic_path: str = ""
    publish_futures: list = []
    custom_retry = api_core.retry.Retry(
        initial=0.250,  # seconds (default: 0.1)
        maximum=90.0,  # seconds (default: 60.0)
        multiplier=1.45,  # default: 1.3
        deadline=300.0,  # seconds (default: 60.0)
        predicate=api_core.retry.if_exception_type(
            api_core.exceptions.Aborted,
            api_core.exceptions.DeadlineExceeded,
            api_core.exceptions.InternalServerError,
            api_core.exceptions.ResourceExhausted,
            api_core.exceptions.ServiceUnavailable,
            api_core.exceptions.Unknown,
            api_core.exceptions.Cancelled,
        ),
    )

    def __init__(self, topic_path):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = topic_path

        if not self.topic_path:
            raise Exception("Topic path is not defined")

        logger.info(f"Initialize publisher {self.publisher.SERVICE_ADDRESS}")

    def publish_message(self, message_dict: dict):
        try:
            string_message = json.dumps(message_dict)
            string_message = string_message.encode("utf-8")
            return self.publisher.publish(topic=self.topic_path, data=string_message, retry=self.custom_retry)
        except RetryError as ex:
            logger.error(f"RetryError: {ex}: {message_dict}")
        except Exception as ex:
            logger.error(f"Exception: {ex}: {message_dict}")
