# standard imports
import logging

# external imports
import pytest

# local imports

logg = logging.getLogger(__file__)


@pytest.fixture(scope="function")
def successful_stk_push_response():
    return {
        "MerchantRequestID": "29115-34620561-1",
        "CheckoutRequestID": "ws_CO_191220191020363925",
        "ResponseCode": 0,
        "ResponseDescription": "Success. Request accepted for processing",
        "CustomerMessage": "Success. Request accepted for processing",
        "ResultCode": 0,
    }


@pytest.fixture(scope="function")
def failed_stk_push_response():
    return {
        "requestId": "1494-250373-3",
        "errorCode": "500.001.1001",
        "errorMessage": "[MerchantValidate] - Wrong credentials"
    }


@pytest.fixture(scope="function")
def successful_stk_push_callback():
    return {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-1",
                "CheckoutRequestID": "ws_CO_191220191020363925",
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {
                            "Name": "Amount",
                            "Value": 1.00
                        },
                        {
                            "Name": "MpesaReceiptNumber",
                            "Value": "NLJ7RT61SV"
                        },
                        {
                            "Name": "TransactionDate",
                            "Value": 20191219102115
                        },
                        {
                            "Name": "PhoneNumber",
                            "Value": 254708374149
                        }]
                }
            }
        }
    }


@pytest.fixture(scope="function")
def failed_stk_push_callback():
    return {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "29115-34620561-1",
                "CheckoutRequestID": "ws_CO_191220191020363925",
                "ResultCode": 1032,
                "ResultDesc": "Request cancelled by user."
            }
        }
    }


@pytest.fixture(scope="function")
def successful_stk_push_status_query():
    return {
        "ResponseCode": 0,
        "ResponseDescription": "The service request has been accepted successfully.",
        "MerchantRequestID": "22205-34066-1",
        "CheckoutRequestID": "ws_CO_13012021093521236557",
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully."
    }


@pytest.fixture(scope="function")
def failed_stk_push_status_query():
    return {
        "ResponseCode": 0,
        "ResponseDescription": "The service request has been accepted successfully",
        "MerchantRequestID": "22679-29098188-1",
        "CheckoutRequestID": "ws_CO_180220220101207943",
        "ResultCode": 1032,
        "ResultDesc": "Request cancelled by user"
    }
