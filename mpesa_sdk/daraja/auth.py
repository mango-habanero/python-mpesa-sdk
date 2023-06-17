"""This module contains the methods for authenticating with the Daraja API."""

# standard imports
import base64
import os

# external imports
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth

# local imports
from mpesa_sdk.exceptions import AuthenticationError
from mpesa_sdk.utils import timestamp
from mpesa_sdk.utils import make_request


def daraja_access_token(consumer_key: str, consumer_secret: str):
    """This method retrieves the access token from the Daraja API.
    :param consumer_key: the consumer key.
    :type consumer_key: str
    :param consumer_secret: the consumer secret.
    :type consumer_secret: str
    :return: the access token.
    :rtype: str
    """
    response = make_request(
        auth=HTTPBasicAuth(consumer_key, consumer_secret),
        method="GET",
        url=os.getenv(
            "OAUTH_URL",
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        ),
    )
    if response is None:
        raise HTTPError("Could not retrieve access token.")

    if response.status_code == 200:
        return response.json().get("access_token")

    error_message = response.json().get("errorMessage")
    raise AuthenticationError(error_message)


def stk_push_password(passkey: str, shortcode: str):
    """This method generates the password for the STK push request.
    :param passkey: the passkey.
    :type passkey: str
    :param shortcode: the shortcode.
    :type shortcode: str
    :return: the password.
    :rtype: str
    """

    password = shortcode + passkey + timestamp()
    return base64.b64encode(password.encode("utf-8")).decode("utf-8")
