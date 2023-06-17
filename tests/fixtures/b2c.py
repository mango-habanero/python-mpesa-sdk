# standard imports

# external imports
import pytest


# local imports

# test imports

@pytest.fixture(scope="function")
def failed_b2c_response():
    return {
        "requestId": "11728-2929992-1",
        "errorCode": "401.002.01",
        "errorMessage": "Error Occurred - Invalid Access Token - BJGFGOXv5aZnw90KkA4TDtu4Xdyf"
    }


@pytest.fixture(scope="function")
def successful_b2c_response():
    return {
        "ConversationID": "AG_20191219_00005797af5d7d75f652",
        "OriginatorConversationID": "16740-34861180-1",
        "ResponseCode": 0,
        "ResponseDescription": "Accept the service request successfully."
    }


@pytest.fixture(scope="function")
def successful_b2c_callback():
    return {
        "Result": {
            "ResultType": 0,
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully.",
            "OriginatorConversationID": "10571-7910404-1",
            "ConversationID": "AG_20191219_00004e48cf7e3533f581",
            "TransactionID": "NLJ41HAY6Q",
            "ResultParameters": {
                "ResultParameter": [
                    {
                        "Key": "TransactionAmount",
                        "Value": 10
                    },
                    {
                        "Key": "TransactionReceipt",
                        "Value": "NLJ41HAY6Q"
                    },
                    {
                        "Key": "B2CRecipientIsRegisteredCustomer",
                        "Value": "Y"
                    },
                    {
                        "Key": "B2CChargesPaidAccountAvailableFunds",
                        "Value": -4510.00
                    },
                    {
                        "Key": "ReceiverPartyPublicName",
                        "Value": "254708374149 - John Doe"
                    },
                    {
                        "Key": "TransactionCompletedDateTime",
                        "Value": "19.12.2019 11:45:50"
                    },
                    {
                        "Key": "B2CUtilityAccountAvailableFunds",
                        "Value": 10116.00
                    },
                    {
                        "Key": "B2CWorkingAccountAvailableFunds",
                        "Value": 900000.00
                    }
                ]
            },
            "ReferenceData": {
                "ReferenceItem": {
                    "Key": "QueueTimeoutURL",
                    "Value": "https:\/\/internalsandbox.safaricom.co.ke\/mpesa\/b2cresults\/v1\/submit"
                }
            }
        }
    }
