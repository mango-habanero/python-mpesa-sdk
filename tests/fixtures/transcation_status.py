# standard imports
import os
import logging

# external imports
import pytest

# local imports

logg = logging.getLogger(__file__)


@pytest.fixture(scope="function")
def successful_transaction_status_query_callback():
    return {
        "Result": {
            "ConversationID": "AG_20180223_0000493344ae97d86f75",
            "OriginatorConversationID": "3213-416199-2",
            "ReferenceData": {
                "ReferenceItem": {
                    "Key": "Occasion"
                }
            },
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully.",
            "ResultParameters": {
                "ResultParameter": [
                    {
                        "Key": "DebitPartyName",
                        "Value": "600310 - Safaricom333"
                    },
                    {
                        "Key": "CreditPartyName",
                        "Value": "254708374149 - John Doe"
                    },
                    {
                        "Key": "OriginatorConversationID",
                        "Value": "3211-416020-3"
                    },
                    {
                        "Key": "InitiatedTime",
                        "Value": 20180223054112
                    },
                    {
                        "Key": "DebitAccountType",
                        "Value": "Utility Account"
                    },
                    {
                        "Key": "DebitPartyCharges",
                        "Value": "Fee For B2C Payment|KES|22.40"
                    },
                    {
                        "Key": "TransactionReason"
                    },
                    {
                        "Key": "ReasonType",
                        "Value": "Business Payment to Customer via API"
                    },
                    {
                        "Key": "TransactionStatus",
                        "Value": "Completed"
                    },
                    {
                        "Key": "FinalisedTime",
                        "Value": 20180223054112
                    },
                    {
                        "Key": "Amount",
                        "Value": 300
                    },
                    {
                        "Key": "ConversationID",
                        "Value": "AG_20180223_000041b09c22e613d6c9"
                    },
                    {
                        "Key": "ReceiptNo",
                        "Value": "MBN31H462N"
                    }
                ]
            },
            "ResultType": 0,
            "TransactionID": "MBN0000000"
        }
    }


@pytest.fixture(scope="function")
def failed_transaction_status_query_response():
    return {
        "requestId": "31359-99802588-1",
        "errorCode": "400.002.02",
        "errorMessage": "Bad Request - Invalid TransactionID"
    }


@pytest.fixture(scope="function")
def successful_transaction_status_query_response():
    return {
        "OriginatorConversationID": "71840-27539181-07",
        "ConversationID": "AG_20210709_12346c8e6f8858d7b70a",
        "ResponseCode": 0,
        "ResponseDescription": "Accept the service request successfully."
    }