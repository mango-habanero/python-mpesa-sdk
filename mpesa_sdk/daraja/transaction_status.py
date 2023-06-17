"""This module implements the transaction status query functionality of the Daraja API."""

# standard imports
import logging
import os
from typing import Union

# local imports
from mpesa_sdk.daraja.enums import CommandID, IdentifierType
from mpesa_sdk.daraja.interfaces import (
    BaseCallbackParser,
    BaseRequestBuilder,
    BaseResponseParser,
)

# external imports

logg = logging.getLogger()


class TransactionStatusQueryRequest(BaseRequestBuilder):
    """This class implements the transaction status query request builder interface."""

    URL_ENV = "TRANSACTION_STATUS_URL"

    def build(
        self,
        identifier_type: IdentifierType,
        initiator: str,
        occasion: str,
        party_a: str,
        remarks: str,
        transaction_id: str,
    ) -> dict[str, Union[str, int]]:  # type: ignore
        """This method builds the transaction status query request.
        :param identifier_type: the identifier type.
        :type identifier_type: IdentifierType
        :param initiator: the initiator.
        :type initiator: str
        :param occasion: the occasion.
        :type occasion: str
        :param party_a: the party a.
        :type party_a: str
        :param remarks: the remarks.
        :type remarks: str
        :param transaction_id: the transaction id.
        :type transaction_id: str
        :return: the transaction status query request.
        :rtype: dict
        """
        return {
            "Initiator": initiator,
            "SecurityCredential": os.getenv(
                "SECURITY_CREDENTIAL", "your-security-credential"
            ),
            "CommandID": CommandID.TRANSACTION_STATUS_QUERY.value,
            "TransactionID": transaction_id,
            "PartyA": party_a,
            "IdentifierType": identifier_type.value,
            "ResultURL": os.getenv(
                "TRANSACTION_STATUS_CALLBACK_URL",
                "https://mydomain.ext/transaction-status-callback-url",
            ),
            "QueueTimeOutURL": os.getenv(
                "TRANSACTION_STATUS_QUEUE_TIMEOUT_URL",
                "https://mydomain.ext/transaction-status-queue-timeout-url",
            ),
            "Remarks": remarks,
            "Occasion": occasion,
        }


class TransactionStatusResponseParser(BaseResponseParser):
    """This class implements the transaction status response parser interface."""

    def get_error_log_message(self) -> str:
        """This method returns the error log message.
        :return: the error log message.
        :rtype: str
        """
        return (
            f"Transaction status query: {self.request_id}, failed. {self.description}."
        )

    def get_success_log_message(self) -> str:
        """This method returns the success log message.
        :return: the success log message.
        :rtype: str
        """
        return f"Transaction status query: {self.request_id}, initiated successfully. {self.description}."


class TransactionStatusCallbackParser(BaseCallbackParser):
    """This class implements the transaction status callback parser interface."""

    def get_error_log_message(self) -> str:
        """This method returns the error log message.
        :return: the error log message.
        :rtype: str
        """
        return f"Transaction status query: {self.transaction_id}, failed. {self.description}."

    def get_success_log_message(self) -> str:
        """This method returns the success log message.
        :return: the success log message.
        :rtype: str
        """
        return f"Transaction status query: {self.transaction_id}, processed successfully. {self.description}."
