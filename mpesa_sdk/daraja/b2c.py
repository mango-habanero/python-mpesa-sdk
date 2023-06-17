"""This module implements the B2C payment request builder, response parser and callback parser interfaces."""

# standard imports
import logging
import os
from typing import Union

# external imports
from mpesa_sdk.daraja.enums import CommandID
from mpesa_sdk.daraja.interfaces import (
    BaseCallbackParser,
    BaseRequestBuilder,
    BaseResponseParser,
)

logg = logging.getLogger()


class B2CPaymentRequest(BaseRequestBuilder):
    """This class implements the B2C payment request builder interface."""

    URL_ENV = "B2C_URL"

    def build(
        self,
        amount: str,
        command_id: CommandID,
        initiator: str,
        occasion: str,
        party_a: str,
        party_b: str,
        remarks: str,
    ) -> dict[str, Union[str, int]]:
        """This method builds the B2C payment request.
        :param amount: the amount.
        :type amount: str
        :param command_id: the command id.
        :type command_id: CommandID
        :param initiator: the initiator.
        :type initiator: str
        :param occasion: the occasion.
        :type occasion: str
        :param party_a: the party a.
        :type party_a: str
        :param party_b: the party b.
        :type party_b: str
        :param remarks: the remarks.
        :type remarks: str
        :return: the B2C payment request.
        :rtype: dict
        """
        return {
            "InitiatorName": initiator,
            "SecurityCredential": os.getenv(
                "SECURITY_CREDENTIAL", "your-security-credential"
            ),
            "CommandID": command_id.value,
            "Amount": amount,
            "PartyA": party_a,
            "PartyB": party_b,
            "Remarks": remarks,
            "QueueTimeOutURL": os.getenv(
                "B2C_QUEUE_TIMEOUT_URL", "https://mydomain.ext/b2c-queue-timeout-url"
            ),
            "ResultURL": os.getenv(
                "B2C_CALLBACK_URL", "https://mydomain.ext/b2c-callback-url"
            ),
            "Occasion": occasion,
        }


class B2CPaymentResponseParser(BaseResponseParser):
    """This class implements the B2C payment response parser interface."""

    def get_error_log_message(self):
        return f"B2C payment request: {self.request_id}, initiation failed. {self.description}."

    def get_success_log_message(self):
        return f"B2C payment request: {self.request_id}, initiated successfully. {self.description}."


class B2CCallbackParser(BaseCallbackParser):
    """This class implements the B2C callback parser interface."""

    def get_error_log_message(self):
        return f"B2C transaction: {self.transaction_id} failed with response: {self.description}."

    def get_success_log_message(self):
        return f"B2C transaction: {self.transaction_id} processed successfully."
