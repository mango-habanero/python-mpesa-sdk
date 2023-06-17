# standard imports
import logging
import os

# external imports
import pytest
from requests_mock import Mocker

# local imports
from mpesa_sdk.daraja.enums import CommandID, IdentifierType
from mpesa_sdk.daraja.transaction_status import (TransactionStatusQueryRequest,
                       TransactionStatusResponseParser,
                       TransactionStatusCallbackParser)
from mpesa_sdk.utils import camel_to_snake

# test imports
from tests.helpers.http import build_response


@pytest.mark.parametrize("identifier_type, initiator, occasion, party_a, remarks, transaction_id", [
    (IdentifierType.MSISDN, "test-api", "Tx oracle instruction", "123456", "Test remarks", "QWEDF4MS007"),
    (IdentifierType.TILL_NUMBER, "test-api", "Pre-processing check", "654321", "Test remarks 1", "QWEDF4MS789"),
    (IdentifierType.ORGANIZATION_SHORT_CODE, "test-api", "Retrial preflight checks", "963258", "Test remarks 2",
     "QWEDF4MS779")
])
def test_transaction_status_query_request(identifier_type, initiator, load_env_vars, occasion, party_a, remarks,
                                          successful_oauth_response, successful_transaction_status_query_response,
                                          transaction_id):
    daraja_oauth_url = os.getenv("OAUTH_URL")

    transaction_status_query_request = TransactionStatusQueryRequest(os.getenv("CONSUMER_KEY"),
                                                                     os.getenv(
                                                                         "CONSUMER_SECRET"),
                                                                     os.getenv("SHORTCODE"))
    expected_payload = {
        "Initiator": initiator,
        "SecurityCredential": os.getenv("SECURITY_CREDENTIAL", "your-security-credential"),
        "CommandID": CommandID.TRANSACTION_STATUS_QUERY.value,
        "TransactionID": transaction_id,
        "PartyA": party_a,
        "IdentifierType": identifier_type.value,
        "ResultURL": os.getenv("TRANSACTION_STATUS_CALLBACK_URL"),
        "QueueTimeOutURL": os.getenv("TRANSACTION_STATUS_QUEUE_TIMEOUT_URL"),
        "Remarks": remarks,
        "Occasion": occasion
    }
    payload = transaction_status_query_request.build(identifier_type, initiator, occasion, party_a, remarks,
                                                     transaction_id)
    assert payload == expected_payload

    with Mocker(real_http=False) as requests_mocker:
        requests_mocker.register_uri("GET", daraja_oauth_url, json=successful_oauth_response, reason="OK",
                                     status_code=200)

        requests_mocker.register_uri("POST", os.getenv("TRANSACTION_STATUS_URL"),
                                     json=successful_transaction_status_query_response,
                                     reason="OK",
                                     status_code=200)
        response = transaction_status_query_request.execute(identifier_type, initiator, occasion, party_a, remarks,
                                                            transaction_id)
        assert response.json() == successful_transaction_status_query_response


def test_transaction_status_query_response_parser(caplog, failed_transaction_status_query_response,
                                                  successful_transaction_status_query_response):
    caplog.set_level(logging.ERROR)
    failed_response = build_response(failed_transaction_status_query_response, "utf-8", "Bad Request", 400)
    transaction_status_query_response_parser = TransactionStatusResponseParser(failed_response)
    parsed_response = transaction_status_query_response_parser.parse()

    description = failed_transaction_status_query_response.get("errorMessage")
    request_id = failed_transaction_status_query_response.get("requestId")

    assert f"Transaction status query: {request_id}, failed. {description}." in caplog.text
    assert parsed_response == {camel_to_snake(key): value for key, value in
                               failed_transaction_status_query_response.items()}

    caplog.set_level(logging.INFO)
    successful_response = build_response(successful_transaction_status_query_response, "utf-8", "OK", 200)
    transaction_status_query_response_parser = TransactionStatusResponseParser(successful_response)
    parsed_response = transaction_status_query_response_parser.parse()

    request_id = successful_transaction_status_query_response.get("OriginatorConversationID")
    description = successful_transaction_status_query_response.get("ResponseDescription")

    assert f"Transaction status query: {request_id}, initiated successfully. {description}" in caplog.text
    assert parsed_response == {camel_to_snake(key): value for key, value in
                               successful_transaction_status_query_response.items()}


def test_transaction_status_query_callback_parser(caplog, successful_transaction_status_query_callback):
    caplog.set_level(logging.INFO)
    transaction_status_query_callback_parser = TransactionStatusCallbackParser(
        successful_transaction_status_query_callback)
    parsed_response = transaction_status_query_callback_parser.parse()

    result = successful_transaction_status_query_callback.get("Result")
    description = result.get("ResultDesc")
    result_code = result.get("ResultCode")
    transaction_id = result.get("TransactionID")
    transaction = result.get("ResultParameters").get("ResultParameter")

    parsed_result_parameters = {
        camel_to_snake(element.get("Key")): element.get("Value")
        for element in transaction
    }

    expected_response = {
        "data": parsed_result_parameters,
        "description": description,
        "success": result_code == 0,
        "transaction_id": transaction_id
    }
    assert parsed_response == expected_response
    assert f"Transaction status query: {transaction_id}, processed successfully. {description}" in caplog.text
