"""This module contains classes for building and parsing STK push payment requests."""

# standard imports
import logging
import os
from typing import Union

# external imports
from requests import Response

# local imports
from .auth import stk_push_password
from .enums import TransactionType
from .interfaces import BaseCallbackParser, BaseRequestBuilder, ResponseParserInterface
from mpesa_sdk.utils import camel_to_snake, preprocess_http_response, timestamp

logg = logging.getLogger()


class StkPushRequestInterface(BaseRequestBuilder):
    """This class contains the interface for building STK push payment requests."""

    def __init__(
        self, consumer_key: str, consumer_secret: str, passkey: str, shortcode: str
    ):
        """This method initializes the STK push payment request builder class.
        :param consumer_key: the consumer key.
        :type consumer_key: str
        :param consumer_secret: the consumer secret.
        :type consumer_secret: str
        :param passkey: the passkey.
        :type passkey: str
        :param shortcode: the shortcode.
        :type shortcode: str
        """
        super().__init__(consumer_key, consumer_secret, shortcode)
        self.passkey = passkey

    @property
    def password(self):
        """This method generates the password.
        :return: the password.
        :rtype: str
        """
        return stk_push_password(self.passkey, self.shortcode)

    def build(self, *args):
        pass


class StkPushResponseParser(ResponseParserInterface):
    """This class contains the interface for parsing STK push payment responses."""

    def __init__(self, response: Response):
        self.response = preprocess_http_response(response)
        if isinstance(self.response, dict):
            self.description = (
                self.response.get("ResultDesc")
                or self.response.get("ResponseDescription")
                or self.response.get("errorMessage")
            )

            try:
                self.request_id = self.response["MerchantRequestID"]
            except KeyError:
                self.request_id = self.response["requestId"]

            try:
                self.result_code = self.response["ResultCode"]
            except KeyError:
                self.result_code = self.response["errorCode"]

    def parse(self):
        if isinstance(self.response, dict):
            if self.result_code == 0:
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


class StkPushPaymentRequest(StkPushRequestInterface):
    """This class implements the STK push payment request builder interface."""

    URL_ENV = "STK_PUSH_INITIATION_URL"

    def build(
        self,
        account_reference: str,
        amount: str,
        recipient: str,
        transaction_description: str,
    ):
        """This method builds the STK push payment request.
        :param account_reference: the account reference.
        :type account_reference: str
        :param amount: the amount.
        :type amount: str
        :param recipient: the recipient.
        :type recipient: str
        :param transaction_description: the transaction description.
        :type transaction_description: str
        :return: the STK push payment request.
        :rtype: dict
        """
        return {
            "BusinessShortCode": self.shortcode,
            "Password": self.password,
            "Timestamp": timestamp(),
            "TransactionType": TransactionType.CUSTOMER_BUY_GOODS_ONLINE.value,
            "Amount": amount,
            "PartyA": recipient,
            "PartyB": self.shortcode,
            "PhoneNumber": recipient,
            "CallBackURL": os.getenv(
                "STK_PUSH_CALLBACK_URL", "https://mydomain.ext/stk-push-callback-url"
            ),
            "AccountReference": account_reference,
            "TransactionDesc": transaction_description,
        }


class StkPushPaymentResponseParser(StkPushResponseParser):
    """This class implements the STK push payment response parser interface."""

    def get_error_log_message(self):
        """Get error log message."""
        return (
            f"STK push payment request: {self.request_id}, failed. {self.description}."
        )

    def get_success_log_message(self):
        """Get success log message."""
        return f"STK push payment request: {self.request_id}, initiated. {self.description}."


class StkPushStatusQueryRequest(StkPushRequestInterface):
    """This class handles the STK push status query request."""

    URL_ENV = "STK_PUSH_STATUS_QUERY_URL"

    def build(self, checkout_request_id: str):
        """This method builds the request payload.
        :param checkout_request_id: The checkout request id.
        :type checkout_request_id: str
        :return: The request payload.
        :rtype: dict
        """
        return {
            "BusinessShortCode": self.shortcode,
            "Password": stk_push_password(self.passkey, self.shortcode),
            "Timestamp": timestamp(),
            "CheckoutRequestID": checkout_request_id,
        }


class StkPushStatusQueryResponseParser(StkPushResponseParser):
    """This class parses the response from the STK push status query request."""

    def get_error_log_message(self):
        """Get error log message."""
        return f"STK push status query request: {self.request_id} failed. {self.description}."

    def get_success_log_message(self):
        """Get success log message."""
        return f"STK push status query request: {self.request_id} processed successfully. {self.description}."


class StkPushCallbackRequestParser(BaseCallbackParser):
    """This class parses the request sent by daraja to the callback url."""

    def __init__(self, request: dict[str, Union[dict, int, dict]]):
        """This method initializes the class.
        :param request: The request sent by daraja to the callback url.
        :type request: dict
        """
        super().__init__(request)
        self.result = request.get("Body").get("stkCallback")
        self.description = self.result.get("ResultDesc")
        if self.result.get("ResultCode") == 0:
            self.transaction = self.result.get("CallbackMetadata").get("Item")
        self.transaction_id = self.result.get("MerchantRequestID")

    def get_error_log_message(self):
        """Get error log message."""
        return f"STK push callback request: {self.transaction_id} failed. {self.description}."

    def get_success_log_message(self):
        """Get success log message."""
        return f"STK push callback request: {self.transaction_id} processed successfully. {self.description}."

    def parse(self) -> dict[str, Union[str, int]]:
        """This method parses the request sent by daraja to the callback url
        :return: A dictionary containing the parsed request.
        :rtype: dict
        """
        parsed_request = super().parse()
        if parsed_request["success"]:
            data = {
                camel_to_snake(element.get("Name")): element.get("Value")
                for element in self.transaction
            }
            parsed_request["data"] = data
        return parsed_request
