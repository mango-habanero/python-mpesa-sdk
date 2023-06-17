"""This module implements the transaction reversal request and response parser interfaces."""

# standard imports
import logging
import os
from typing import Union

# local imports
from mpesa_sdk.daraja.enums import CommandID
from mpesa_sdk.daraja.interfaces import (
    BaseCallbackParser,
    BaseRequestBuilder,
    BaseResponseParser,
)

# external imports

logg = logging.getLogger()


class ReversalRequest(BaseRequestBuilder):
    """This class implements the transaction reversal request builder interface."""

    URL_ENV = "REVERSAL_URL"

    def build(
        self,
        amount: float,
        initiator: str,
        occasion: str,
        receiver_party: str,
        remarks: str,
        transaction_id: str,
    ) -> dict[str, Union[str, int]]:
        """This method builds the transaction reversal request.
        :param amount: the amount.
        :type amount: float
        :param initiator: the initiator.
        :type initiator: str
        :param occasion: the occasion.
        :type occasion: str
        :param receiver_party: the receiver party.
        :type receiver_party: str
        :param remarks: the remarks.
        :type remarks: str
        :param transaction_id: the transaction id.
        :type transaction_id: str
        :return: the transaction reversal request.
        :rtype: dict
        """
        return {
            "Initiator": initiator,
            "SecurityCredential": os.getenv(
                "SECURITY_CREDENTIAL", "your-security-credential"
            ),
            "CommandID": CommandID.TRANSACTION_REVERSAL.value,
            "TransactionID": transaction_id,
            "Amount": amount,
            "ReceiverParty": receiver_party,
            "ReceiverIdentifierType": "11",
            "ResultURL": os.getenv(
                "REVERSAL_CALLBACK_URL", "https://mydomain.ext/reversal-callback-url"
            ),
            "QueueTimeOutURL": os.getenv(
                "REVERSAL_QUEUE_TIMEOUT_URL",
                "https://mydomain.ext/reversal-queue-timeout-url",
            ),
            "Remarks": remarks,
            "Occasion": occasion,
        }


class ReversalResponseParser(BaseResponseParser):
    """This class implements the transaction reversal response parser interface."""

    def get_success_log_message(self) -> str:
        return f"Reversal request: {self.request_id}, initiated successfully with description: {self.description}."

    def get_error_log_message(self) -> str:
        return f"Reversal request: {self.request_id}, initiation failed with description: {self.description}."


class ReversalRequestCallbackParser(BaseCallbackParser):
    """This class implements the transaction reversal request callback parser interface."""

    def get_success_log_message(self) -> str:
        return f"Reversal request for transaction: {self.transaction_id} processed successfully."

    def get_error_log_message(self) -> str:
        return f"Reversal request: {self.transaction_id}, failed with description: {self.description}."
