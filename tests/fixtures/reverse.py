# standard imports
import os
import logging

# external imports
import pytest

# local imports

logg = logging.getLogger(__file__)


@pytest.fixture(scope="function")
def successful_reversal_callback():
    return {
        "Result": {
            "ResultType": 0,
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully",
            "OriginatorConversationID": "8521-4298025-1",
            "ConversationID": "AG_20181005_00004d7ee675c0c7ee0b",
            "TransactionID": "MJ561H6X5O",
            "ResultParameters": {
                "ResultParameter": [
                    {
                        "Key": "DebitAccountBalance",
                        "Value": "Utility Account|KES|51661.00|51661.00|0.00|0.00"
                    },
                    {
                        "Key": "Amount",
                        "Value": 100
                    },
                    {
                        "Key": "TransCompletedTime",
                        "Value": 20181005153225
                    },
                    {
                        "Key": "OriginalTransactionID",
                        "Value": "MJ551H6X5D"
                    },
                    {
                        "Key": "Charge",
                        "Value": 0
                    },
                    {
                        "Key": "CreditPartyPublicName",
                        "Value": "254708374149 - John Doe"
                    },
                    {
                        "Key": "DebitPartyPublicName",
                        "Value": "601315 - Safaricom1338"
                    }
                ]
            },
            "ReferenceData": {
                "ReferenceItem": {
                    "Key": "QueueTimeoutURL",
                    "Value": "https://internalsandbox.safaricom.co.ke/mpesa/reversalresults/v1/submit"
                }
            }
        }
    }


@pytest.fixture(scope="function")
def failed_reversal_response():
    return {
        "requestId": "31359-99802588-1",
        "errorCode": "400.002.02",
        "errorMessage": "Bad Request - Invalid TransactionID"
    }


@pytest.fixture(scope="function")
def successful_reversal_response():
    return {
        "OriginatorConversationID": "71840-27539181-07",
        "ConversationID": "AG_20210709_12346c8e6f8858d7b70a",
        "ResponseCode": 0,
        "ResponseDescription": "Accept the service request successfully."
    }
