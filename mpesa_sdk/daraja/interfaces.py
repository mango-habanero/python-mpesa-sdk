"""This module contains interfaces used by the SDK."""

# standard imports
import logging
import os
from abc import ABC, abstractmethod
from typing import Union

# external imports
from requests import Response

from mpesa_sdk.utils import camel_to_snake, make_request, preprocess_http_response

# local imports
from .auth import daraja_access_token

logg = logging.getLogger()


# pylint: disable=too-few-public-methods
class CallbackParserInterface(ABC):
    """This class contains the interface for parsing callbacks."""

    def parse(self):
        """This method parses the callback.
        :return: parsed callback
        :rtype: dict
        :raises: NotImplementedError
        """
        raise NotImplementedError()


class RequestBuilderInterface(ABC):
    """This class contains the interface for building requests."""

    @abstractmethod
    def authenticate(self):
        """This method authenticates the request.
        :rtype: dict
        :raises: NotImplementedError
        """
        raise NotImplementedError()

    @abstractmethod
    def build(self, *args):
        """This method builds the request.
        :param args: request parameters.
        :type args: dict
        :return: the request.
        :rtype: dict
        :raises: NotImplementedError
        """
        raise NotImplementedError()

    @abstractmethod
    def execute(self, *args):
        """This method executes the request.
        :param args: request parameters.
        :type args: dict
        :return: response
        :rtype: requests.Response
        :raises: NotImplementedError
        """
        raise NotImplementedError()


# pylint: disable=too-few-public-methods
class ResponseParserInterface(ABC):
    """This class contains the interface for parsing responses."""

    @abstractmethod
    def parse(self):
        """This method parses the response.
        :return: parsed response
        :rtype: dict
        :raises: NotImplementedError
        """
        raise NotImplementedError()


class BaseCallbackParser(CallbackParserInterface):
    """This class is the base callback parser."""

    def __init__(self, request: dict[str, dict]):
        """This method initializes the base callback parser class.
        :param request: the request.
        :type request: dict
        """
        self.request = request
        self.result = self.request.get("Result")
        if self.result:
            self.description = self.result.get("ResultDesc")
            if result_parameters := self.result.get("ResultParameters"):
                self.transaction = result_parameters.get("ResultParameter")
            self.transaction_id = self.result.get("TransactionID")

    def parse(self):
        """This method parses the callback.
        :return: the parsed callback.
        :rtype: dict
        """
        result_code = self.result["ResultCode"]
        parsed_response = {
            "description": self.description,
            "success": result_code == 0,
            "transaction_id": self.transaction_id,
        }

        if result_code == 0:
            logg.info(self.get_success_log_message())
            data = {
                camel_to_snake(element.get("Key")): element.get("Value")
                for element in self.transaction
                if element.get("Key")
            }
            parsed_response["data"] = data
        else:
            logg.error(self.get_error_log_message())

        return parsed_response

    def get_error_log_message(self):
        """Get error log message."""
        raise NotImplementedError

    def get_success_log_message(self):
        """Get success log message."""
        raise NotImplementedError


class BaseRequestBuilder(RequestBuilderInterface):
    """This is a base payment request class that implements common methods"""

    URL_ENV = "URL_ENV"

    def __init__(self, consumer_key: str, consumer_secret: str, shortcode: str):
        """This method initializes the base payment request class.
        :param consumer_key: the consumer key.
        :type consumer_key: str
        :param consumer_secret: the consumer secret.
        :type consumer_secret: str
        :param shortcode: the shortcode.
        :type shortcode: str
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.shortcode = shortcode

    def authenticate(self):
        """This method authenticates the payment request.
        :return: the authentication headers.
        :rtype: dict
        """
        access_token = daraja_access_token(
            consumer_key=self.consumer_key, consumer_secret=self.consumer_secret
        )
        return {"Authorization": f"Bearer {access_token}"}

    def build(self, *args):
        """This method builds the payment request.
        :return: the payment request.
        :rtype: dict
        """
        raise NotImplementedError

    def execute(self, *args):
        """This method executes the payment request.
        :return: response
        :rtype: requests.Response
        """
        payload = self.build(*args)
        auth_headers = self.authenticate()
        headers = {"Content-Type": "application/json", **auth_headers}
        return make_request(
            "POST", os.environ.get(self.URL_ENV), headers=headers, json=payload
        )


class BaseResponseParser(ResponseParserInterface):
    """This class is the base response parser."""

    def __init__(self, response: Response):
        """This method initializes the base response parser class.
        :param response: the response.
        :type response: Response
        """

        self.response = preprocess_http_response(response)
        if self.response:
            try:
                self.description = self.response["ResponseDescription"]
            except KeyError:
                self.description = self.response["errorMessage"]

            try:
                self.request_id = self.response["OriginatorConversationID"]
            except KeyError:
                self.request_id = self.response["requestId"]

            try:
                self.response_code = self.response["ResponseCode"]
            except KeyError:
                self.response_code = self.response["errorCode"]

    def parse(self) -> dict[str, Union[str, int]]:
        """This method parses the response.
        :return: the parsed response.
        :rtype: dict
        """

        if self.response_code == 0:
            logg.info(self.get_success_log_message())
        else:
            logg.error(self.get_error_log_message())

        return {camel_to_snake(key): value for key, value in self.response.items()}

    def get_error_log_message(self):
        """Get error log message."""
        raise NotImplementedError

    def get_success_log_message(self):
        """Get success log message."""
        raise NotImplementedError
