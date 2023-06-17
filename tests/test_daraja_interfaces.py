# standard imports
import os

# external imports
import pytest
from requests_mock import Mocker

# local imports
from mpesa_sdk.daraja.interfaces import BaseResponseParser, BaseRequestBuilder
from mpesa_sdk.daraja.auth import daraja_access_token

# test imports
from tests.helpers.http import build_response


def test_request_builder_interface(load_env_vars, successful_oauth_response):
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    daraja_oauth_url = os.getenv("OAUTH_URL")
    shortcode = os.getenv("SHORTCODE")

    request_builder_interface = BaseRequestBuilder(consumer_key, consumer_secret, shortcode)

    with Mocker(real_http=False) as requests_mocker:
        requests_mocker.register_uri("GET", daraja_oauth_url, json=successful_oauth_response, reason="OK",
                                     status_code=200)

        access_token = daraja_access_token(consumer_key, consumer_secret)
        assert request_builder_interface.authenticate() == { "Authorization": f"Bearer {access_token}" }


    with pytest.raises(NotImplementedError):
        request_builder_interface.execute()


def test_response_parser(failed_stk_push_response):
    sample_response = build_response(failed_stk_push_response, "utf-8", "Server Error", 500)
    response_parser = BaseResponseParser(sample_response)
    with pytest.raises(NotImplementedError):
        response_parser.parse()
