# standard imports
import logging
import os

# external imports
import pytest
from requests_mock import Mocker

# local imports
from mpesa_sdk.daraja.enums import CommandID
from mpesa_sdk.daraja.reverse import (ReversalRequest,
                       ReversalResponseParser,
                       ReversalRequestCallbackParser)
from mpesa_sdk.utils import camel_to_snake

# test imports
from tests.helpers.http import build_response


@pytest.mark.parametrize("amount, initiator, occasion, receiver_party, remarks, transaction_id", [
    (25.0, "test-api", "Erroneous transfer", "123456", "Test remarks", "QWEDF4MS007"),
    (25.0, "test-api", "Redemption API error", "654321", "Test remarks", "QWEDF4MS789")
])
def test_reversal_request(amount, initiator, load_env_vars, occasion, receiver_party, remarks,
                          successful_oauth_response, successful_reversal_response, transaction_id):
    daraja_oauth_url = os.getenv("OAUTH_URL")

    stk_push_payment_request = ReversalRequest(os.getenv("CONSUMER_KEY"),
                                               os.getenv("CONSUMER_SECRET"),
                                               os.getenv("SHORTCODE"))
    expected_payload = {
        "Initiator": initiator,
        "SecurityCredential": os.getenv("SECURITY_CREDENTIAL", "your-security-credential"),
        "CommandID": CommandID.TRANSACTION_REVERSAL.value,
        "TransactionID": transaction_id,
        "Amount": amount,
        "ReceiverParty": receiver_party,
        "ReceiverIdentifierType": "11",
        "ResultURL": os.getenv("REVERSAL_CALLBACK_URL"),
        "QueueTimeOutURL": os.getenv("REVERSAL_QUEUE_TIMEOUT_URL"),
        "Remarks": remarks,
        "Occasion": occasion
        }
    payload = stk_push_payment_request.build(amount, initiator, occasion, receiver_party, remarks, transaction_id)
    assert payload == expected_payload

    with Mocker(real_http=False) as requests_mocker:
        requests_mocker.register_uri("GET", daraja_oauth_url, json=successful_oauth_response, reason="OK",
                                     status_code=200)

        requests_mocker.register_uri("POST", os.getenv("REVERSAL_URL"),
                                     json=successful_reversal_response,
                                     reason="OK",
                                     status_code=200)
        response = stk_push_payment_request.execute(amount, initiator, occasion, receiver_party, remarks,
                                                    transaction_id)
        assert response.json() == successful_reversal_response


def test_reversal_response_parser(caplog, failed_reversal_response, successful_reversal_response):
    caplog.set_level(logging.ERROR)
    failed_response = build_response(failed_reversal_response, "utf-8", "Bad Request", 400)
    reversal_response_parser = ReversalResponseParser(failed_response)
    parsed_response = reversal_response_parser.parse()
    error_message = parsed_response.get("error_message")
    request_id = parsed_response.get("request_id")
    assert f"Reversal request: {request_id}, initiation failed with description: {error_message}." in caplog.text
    assert parsed_response == {camel_to_snake(key): value for key, value in failed_reversal_response.items()}

    caplog.set_level(logging.INFO)
    successful_response = build_response(successful_reversal_response, "utf-8", "OK", 200)
    reversal_response_parser = ReversalResponseParser(successful_response)
    parsed_response = reversal_response_parser.parse()
    response_description = parsed_response.get("response_description")
    request_id = parsed_response.get("originator_conversation_id")
    assert f"Reversal request: {request_id}, initiated successfully with description: {response_description}." in caplog.text
    assert parsed_response == {camel_to_snake(key): value for key, value in successful_reversal_response.items()}


def test_reversal_callback_parser(caplog, successful_reversal_callback):
    caplog.set_level(logging.INFO)

    reversal_callback_parser = ReversalRequestCallbackParser(successful_reversal_callback)
    parsed_response = reversal_callback_parser.parse()

    result = successful_reversal_callback.get("Result")
    description = result.get("ResultDesc")
    result_code = result.get("ResultCode")
    transaction_id = result.get("TransactionID")
    transaction = result.get("ResultParameters").get("ResultParameter")

    data = {
        camel_to_snake(element.get("Key")): element.get("Value")
        for element in transaction
    }

    expected_response = {
        "data": data,
        "description": description,
        "success": result_code == 0,
        "transaction_id": transaction_id,
    }

    assert parsed_response == expected_response
    assert f"Reversal request for transaction: {transaction_id} processed successfully." in caplog.text


