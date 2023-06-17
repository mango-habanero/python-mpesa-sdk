# standard imports
import base64
import os

# external imports
import pytest
from requests.exceptions import HTTPError
from requests_mock import Mocker

# local imports
from mpesa_sdk.daraja.auth import daraja_access_token, stk_push_password
from mpesa_sdk.exceptions import AuthenticationError
from mpesa_sdk.utils import timestamp


# test imports

def test_successful_daraja_access_token_retrieval(failed_oauth_response, load_env_vars, mocker, successful_oauth_response):
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    daraja_oauth_url = os.getenv("OAUTH_URL")

    # test successful attempt
    with Mocker(real_http=False) as requests_mocker:
        requests_mocker.register_uri("GET", daraja_oauth_url, json=successful_oauth_response, reason="OK",
                                     status_code=200)
        access_token = daraja_access_token(consumer_key, consumer_secret)
        assert access_token == successful_oauth_response.get("access_token")

    # test erroneous attempt
    with pytest.raises(AuthenticationError) as error:
        with Mocker(real_http=False) as requests_mocker:
            requests_mocker.register_uri("GET", daraja_oauth_url, json=failed_oauth_response, reason="Bad Request",
                                         status_code=400)
            daraja_access_token(consumer_key, consumer_secret)
    assert str(error.value) == failed_oauth_response.get("errorMessage")

    # test failed attempt
    with pytest.raises(HTTPError) as error:
        mocker.patch("requests.get", return_value=None)
        daraja_access_token(consumer_key, consumer_secret)
    assert str(error.value) == "Could not retrieve access token."


def test_stk_push_password(load_env_vars):
    passkey = os.getenv('PASSKEY')
    shortcode = os.getenv("SHORTCODE")
    password = stk_push_password(passkey, shortcode)
    decoded_password = base64.b64decode(password).decode("utf-8")
    assert decoded_password.startswith(shortcode)
    assert passkey in decoded_password
    shortened_timestamp = timestamp()[:8]
    assert shortened_timestamp in decoded_password
