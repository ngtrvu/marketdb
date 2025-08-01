import logging
import json
import redis
from redis.cluster import RedisCluster


def init_redis_pool(
    redis_host="localhost", redis_port=6379, cluster_mode=False, redis_db=0
) -> RedisCluster:
    if cluster_mode:
        redis_c = RedisCluster(host=redis_host, port=redis_port, decode_responses=True)
    else:
        redis_c = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

    try:
        redis_c.ping()

        logging.debug(f'Successfully connected to redis "{redis_host}"')
        return redis_c
    except redis.exceptions.ConnectionError as r_con_error:
        logging.error(f"Redis connection error {r_con_error}")


class RedisCache:
    """Stores and Retrieves data from Redis Hash"""

    def __init__(self, redis_connection):
        self._redis = redis_connection

    def set_multiple(self, key: str, info: dict):
        """
        Set multiple hash fields to multiple values.
        dict can be passed as mapping kwarg:
        :param key:
        :param info:
        :return:
        """
        return self._redis.hmset(key, info)

    def len(self, key: str):
        """
        Get the number of fields in a given hash.
        :param key:
        :return: int:
        """
        return self._redis.hlen(key)

    def get(self, key: str):
        """
        Get all the fields and values in a hash.
        :param key:
        :return: dict:
        """
        return self._redis.hgetall(key)

    def get_all(self, key: str):
        """
        Get all the fields and values in a hash.
        :param key:
        :return: dict:
        """
        return self._redis.hgetall(key)

    def get_multi_keys(self, keys: list):
        return self._redis.mget(keys)

    def publish(self, channel: str, message: dict):
        data = json.dumps(message, sort_keys=True, default=str)
        logging.debug(f"{channel} {message}")
        return self._redis.publish(channel=channel, message=data)

    def subscribe(self, channel: str) -> dict:
        message = self._redis.subscribe(channel=channel)
        logging.debug(f"{channel} {message}")
        return message
