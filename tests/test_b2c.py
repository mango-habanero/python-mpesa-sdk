# standard imports
import logging
import os

# external imports
import pytest
from requests_mock import Mocker

# local imports
from mpesa_sdk.daraja.enums import CommandID
from mpesa_sdk.daraja.b2c import (B2CPaymentRequest,
                       B2CPaymentResponseParser,
                       B2CCallbackParser)
from mpesa_sdk.utils import camel_to_snake

# test imports
from tests.helpers.http import build_response


@pytest.mark.parametrize("amount, command_id, initiator, occasion, party_a, party_b, remarks", [
    ("25", CommandID.BUSINESS_PAYMENT, "test-api", "Test occasion", "632547", "254712345678", "Test Remarks"),
    ("55", CommandID.PROMOTION_PAYMENT, "sample-api", "Test occasion 1", "5647895", "254798765432", "Test Remarks"),
    ("100", CommandID.SALARY_PAYMENT, "test-api", "Test occasion 2", "3654875", "254765432187", "Test Remarks")
])
def test_b2c_request(amount, command_id, initiator, occasion, load_env_vars, party_a, party_b, remarks,
                     successful_oauth_response, successful_b2c_response):
    daraja_oauth_url = os.getenv("OAUTH_URL")

    b2c_payment_request = B2CPaymentRequest(os.getenv("CONSUMER_KEY"),
                                            os.getenv("CONSUMER_SECRET"),
                                            os.getenv("SHORTCODE"))
    expected_payload = {
        "InitiatorName": initiator,
        "SecurityCredential": os.getenv("SECURITY_CREDENTIAL", "your-security-credential"),
        "CommandID": command_id.value,
        "Amount": amount,
        "PartyA": party_a,
        "PartyB": party_b,
        "Remarks": remarks,
        "QueueTimeOutURL": os.getenv("B2C_QUEUE_TIMEOUT_URL"),
        "ResultURL": os.getenv("B2C_CALLBACK_URL"),
        "Occasion": occasion
    }
    payload = b2c_payment_request.build(amount, command_id, initiator, occasion, party_a, party_b, remarks)
    assert payload == expected_payload

    with Mocker(real_http=False) as requests_mocker:
        requests_mocker.register_uri("GET", daraja_oauth_url, json=successful_oauth_response, reason="OK",
                                     status_code=200)

        requests_mocker.register_uri("POST", os.getenv("B2C_URL"),
                                     json=successful_b2c_response,
                                     reason="OK",
                                     status_code=200)
        response = b2c_payment_request.execute(amount, command_id, initiator, occasion, party_a, party_b, remarks)
        assert response.json() == successful_b2c_response


def test_b2c_response_parser(caplog, failed_b2c_response, successful_b2c_response):
    caplog.set_level(logging.ERROR)
    failed_response = build_response(failed_b2c_response, "utf-8", "Bad Request", 400)
    b2c_response_parser = B2CPaymentResponseParser(failed_response)
    parsed_response = b2c_response_parser.parse()
    error_message = parsed_response.get("error_message")
    request_id = parsed_response.get("request_id")
    assert f"B2C payment request: {request_id}, initiation failed. {error_message}." in caplog.text
    assert parsed_response == {camel_to_snake(key): value for key, value in failed_b2c_response.items()}

    caplog.set_level(logging.INFO)
    successful_response = build_response(successful_b2c_response, "utf-8", "OK", 200)
    b2c_response_parser = B2CPaymentResponseParser(successful_response)
    parsed_response = b2c_response_parser.parse()
    response_description = parsed_response.get("response_description")
    request_id = parsed_response.get("originator_conversation_id")
    assert f"B2C payment request: {request_id}, initiated successfully. {response_description}." in caplog.text
    assert parsed_response == {camel_to_snake(key): value for key, value in successful_b2c_response.items()}


def test_b2c_callback_parser(caplog, successful_b2c_callback):
    caplog.set_level(logging.INFO)
    b2c_callback_parser = B2CCallbackParser(successful_b2c_callback)
    data = {
        camel_to_snake(element.get("Key")): element.get("Value")
        for element in successful_b2c_callback.get('Result').get("ResultParameters").get("ResultParameter")
    }
    transaction_id = successful_b2c_callback.get('Result').get('TransactionID')
    expected_result = {
        "description": successful_b2c_callback.get('Result').get('ResultDesc'),
        "data": data,
        "success": successful_b2c_callback.get('Result').get('ResultCode') == 0,
        "transaction_id": transaction_id
    }
    assert b2c_callback_parser.parse() == expected_result
    assert f"B2C transaction: {transaction_id} processed successfully." in caplog.text

