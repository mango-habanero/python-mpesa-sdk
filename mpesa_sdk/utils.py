"""This module contains utility functions used by the SDK."""

# standard imports
import logging
import os
import re
from datetime import datetime
from typing import Optional

# external imports
import requests
from pytz import timezone

# local imports
from mpesa_sdk.exceptions import UnsupportedMethodError

logg = logging.getLogger(__file__)


def camel_to_snake(value: str):
    """This function converts a camel case string to snake case.
    :param value: string to be converted
    :type value: str
    :return: snake case string
    :rtype: str
    """
    value = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", value).lower()


def make_request(
    method: str,
    url: str,
    data: Optional[dict] = None,
    headers: Optional[dict] = None,
    **kwargs,
):
    """This function makes the actual HTTP request to the API.
    :param method: The HTTP method to use.
    :type method: str
    :param url: The URL to make the request to.
    :type url: str
    :param data: The data to send with the request.
    :type data: dict
    :param headers: The headers to send with the request.
    :type headers: dict
    :return: The response object.
    :rtype: requests.Response
    """
    if method == "GET":
        logg.debug("Retrieving data from: %s.", url)
        result = requests.get(timeout=2, url=url, **kwargs)
    elif method == "POST":
        logg.debug("Posting to: %s with: %s.", url, data)
        result = requests.post(data=data, headers=headers, timeout=2, url=url, **kwargs)
    elif method == "PUT":
        logg.debug("Putting to: %s with: %s.", url, data)
        result = requests.put(data=data, headers=headers, timeout=2, url=url, **kwargs)
    else:
        raise UnsupportedMethodError(f"Unsupported method: {method}.")
    return result


def preprocess_http_response(response: requests.Response) -> Optional[dict]:
    """This function preprocesses the HTTP response and returns the response as a JSON object.
    :param response: The HTTP response object.
    :type response: requests.Response
    :return: The response as a JSON object.
    :rtype: dict
    """
    status_code = response.status_code
    reason = response.reason

    if 100 <= status_code < 200:
        logg.error("Informational errors: %s, reason: %s.", status_code, reason)

    elif 300 <= status_code < 400:
        logg.error("Redirect Issues: %s, reason: %s.", status_code, reason)

    elif 400 <= status_code < 500:
        logg.error("Client Error: %s, reason: %s.", status_code, reason)

    elif 500 <= status_code < 600:
        logg.error("Server Error: %s, reason: %s.", status_code, reason)

    elif status_code == 200:
        logg.info("Request was successful, returning response.")

    return response.json() or None


def timestamp():
    """This function returns the current timestamp in the format required by the API.
    :return: timestamp in the format %Y%m%d%H%M%S. e.g. 20191010120000
    :rtype: str
    """
    timestamp_format = "%Y%m%d%H%M%S"
    zone = os.getenv("TIMEZONE")
    sys_timestamp = datetime.now(timezone(zone))
    return sys_timestamp.strftime(timestamp_format)
