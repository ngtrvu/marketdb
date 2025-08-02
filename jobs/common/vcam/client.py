import json
import logging
import http.client
from urllib.parse import urlencode

import requests

from common.vcam.api import BUSINESS_PERFORMANCE_V2, FUND_PERFORMANCE_V2
from common.vcam.config import VCAMConfig


class VCAMClient(object):

    def __init__(self, _config: VCAMConfig):
        self._header = {
            "Content-Type": "application/json",
            "Authorization": _config.api_token,
            "Access-Code": _config.access_code,
            "APP-Version": _config.app_version,
            "APP-Locale": _config.app_locale,
            "App-Name": _config.app_name,
        }
        self._config = _config

    def _make_get_request(self, _url, _req_body=None, _object=None):
        _header = self._header
        _req_body = json.dumps(_req_body)

        _api_url = self._config.url + _url + '?' + urlencode({'params': _object})
        logging.info(f"_api_url=[{_api_url}] params={_object}")
        _response_obj = requests.get(_api_url, headers=_header, data=_req_body)
        _response = json.loads(_response_obj.content)

        return _response

    def _make_get_request_v2(self, _url, _req_body=None, _object=None):
        _header = self._header

        _req_body = json.dumps(_req_body)

        _api_url = _url + '?' + urlencode({'params': _object})
        logging.info(f"_api_url=[{self._config.host}{_api_url}] params={_object}")

        conn = http.client.HTTPSConnection(self._config.host)
        conn.request(method="GET", url=_api_url,body=_req_body, headers=_header)
        _response_obj = conn.getresponse()
        json_data_string = _response_obj.read()
        json_data_string = json_data_string.decode("utf-8")
        json_data_string
        _response = json.loads(json_data_string)

        return _response

    def business_performance(self, _input_data, _object):
        return self._make_get_request(BUSINESS_PERFORMANCE_V2, _req_body=_input_data,
                                      _object=_object)

    def fund_performance(self, _input_data, _object):
        return self._make_get_request(FUND_PERFORMANCE_V2, _req_body=_input_data,
                                      _object=_object)