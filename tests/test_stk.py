# standard imports
import logging
import os

# external imports

import pytest
from requests_mock import Mocker

# local imports
from mpesa_sdk.daraja.auth import daraja_access_token, stk_push_password
from mpesa_sdk.daraja.enums import TransactionType
from mpesa_sdk.daraja.stk import (StkPushRequestInterface,
                       StkPushPaymentRequest,
                       StkPushStatusQueryRequest,
                       StkPushStatusQueryResponseParser,
                       StkPushPaymentResponseParser,
                       StkPushCallbackRequestParser)
from mpesa_sdk.utils import camel_to_snake, timestamp

# test imports
from tests.helpers.http import build_response


def test_stk_interface(load_env_vars, successful_oauth_response):
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    daraja_oauth_url = os.getenv("OAUTH_URL")
    passkey = os.getenv("PASSKEY")
    shortcode = os.getenv("SHORTCODE")

    stk_push_interface = StkPushRequestInterface(consumer_key, consumer_secret, passkey, shortcode)
    with Mocker(real_http=False) as requests_mocker:
        requests_mocker.register_uri("GET", daraja_oauth_url, json=successful_oauth_response, reason="OK",
                                     status_code=200)
        access_token = daraja_access_token(consumer_key, consumer_secret)
        auth_token = stk_push_interface.authenticate()
        assert auth_token.get("Authorization")[7:] == access_token


@pytest.mark.parametrize("account_reference, amount, recipient, transaction_description", [
    ("some-ref", "100", "254712365478", "Request payment for airtime purchase."),
    ("some-ref", "789", "254787654321", "Request payment to process send money request.")
])
def test_stk_push_payment_request(account_reference, amount, load_env_vars, recipient, successful_oauth_response,
                                  successful_stk_push_response, transaction_description):
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    daraja_oauth_url = os.getenv("OAUTH_URL")
    passkey = os.getenv("PASSKEY")
    shortcode = os.getenv("SHORTCODE")
    stk_push_callback_url = os.getenv("STK_PUSH_CALLBACK_URL")
    stk_push_initiation_url = os.getenv("STK_PUSH_INITIATION_URL")

    stk_push_payment_request = StkPushPaymentRequest(consumer_key, consumer_secret, passkey, shortcode)
    expected_payload = {
        "BusinessShortCode": shortcode,
        "Password": stk_push_payment_request.password,
        "Timestamp": timestamp(),
        "TransactionType": TransactionType.CUSTOMER_BUY_GOODS_ONLINE.value,
        "Amount": amount,
        "PartyA": recipient,
        "PartyB": shortcode,
        "PhoneNumber": recipient,
        "CallBackURL": stk_push_callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_description
    }
    payload = stk_push_payment_request.build(account_reference, amount, recipient, transaction_description)
    assert payload == expected_payload

    with Mocker(real_http=False) as requests_mocker:
        requests_mocker.register_uri("GET", daraja_oauth_url, json=successful_oauth_response, reason="OK",
                                     status_code=200)

        requests_mocker.register_uri("POST", stk_push_initiation_url, json=successful_stk_push_response, reason="OK",
                                     status_code=200)
        response = stk_push_payment_request.execute(account_reference, amount, recipient, transaction_description)
        assert response.json() == successful_stk_push_response


def test_stk_push_transaction_status_query_request(load_env_vars, successful_oauth_response, successful_stk_push_status_query):
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    daraja_oauth_url = os.getenv("OAUTH_URL")
    passkey = os.getenv("PASSKEY")
    shortcode = os.getenv("SHORTCODE")
    stk_push_transaction_status_query = os.getenv("STK_PUSH_STATUS_QUERY_URL")
    checkout_request_id = successful_stk_push_status_query.get("CheckoutRequestID")

    stk_push_transaction_status_query_request = StkPushStatusQueryRequest(consumer_key, consumer_secret,
                                                                          passkey, shortcode)
    expected_payload = {
        "BusinessShortCode": shortcode,
        "Password": stk_push_password(passkey, shortcode),
        "Timestamp": timestamp(),
        "CheckoutRequestID": checkout_request_id
    }
    payload = stk_push_transaction_status_query_request.build(checkout_request_id)
    assert expected_payload == payload

    with Mocker(real_http=False) as requests_mocker:
        requests_mocker.register_uri("GET", daraja_oauth_url, json=successful_oauth_response, reason="OK",
                                     status_code=200)

        requests_mocker.register_uri("POST", stk_push_transaction_status_query,
                                     json=successful_stk_push_status_query, reason="OK", status_code=200)

        response = stk_push_transaction_status_query_request.execute(checkout_request_id)
        assert response.json() == successful_stk_push_status_query


def test_stk_response_parser(caplog, failed_stk_push_response, successful_stk_push_response):
    caplog.set_level(logging.INFO)
    successful_response = build_response(successful_stk_push_response, "utf-8", "OK", 200)
    stk_push_response_parser = StkPushPaymentResponseParser(successful_response)
    expected_parsed_response = {
        camel_to_snake(key): value for key, value in successful_stk_push_response.items()
    }
    parsed_response = stk_push_response_parser.parse()
    response_description = successful_stk_push_response.get("ResponseDescription")
    request_id = successful_stk_push_response.get("MerchantRequestID")
    assert expected_parsed_response == parsed_response
    assert f"STK push payment request: {request_id}, initiated. {response_description}." in caplog.text

    caplog.set_level(logging.ERROR)
    failed_response = build_response(failed_stk_push_response, "utf-8", "Server error", 500)
    stk_push_response_parser = StkPushPaymentResponseParser(failed_response)
    stk_push_response_parser.parse()
    response_description = failed_stk_push_response.get("errorMessage")
    checkout_request_id = failed_stk_push_response.get("requestId")
    assert f"STK push payment request: {checkout_request_id}, failed. {response_description}" in caplog.text


def test_stk_push_callback_request_parser(caplog, failed_stk_push_callback, successful_stk_push_callback):
    caplog.set_level(logging.INFO)
    stk_push_callback_response_parser = StkPushCallbackRequestParser(successful_stk_push_callback)
    parsed_result = stk_push_callback_response_parser.parse()

    result = successful_stk_push_callback.get("Body").get("stkCallback")
    transaction = result.get("CallbackMetadata").get("Item")
    transaction_id = result.get("MerchantRequestID")
    result_code = result.get("ResultCode")
    description = result.get("ResultDesc")

    data = {
        camel_to_snake(element.get("Name")): element.get("Value")
        for element in transaction
    }

    expected_result = {
        "data": data,
        "description": description,
        "success": result_code == 0,
        "transaction_id": transaction_id
    }

    assert expected_result == parsed_result
    assert f"STK push callback request: {transaction_id} processed successfully. {description}." in caplog.text

    caplog.set_level(logging.ERROR)
    stk_push_callback_response_parser = StkPushCallbackRequestParser(failed_stk_push_callback)
    parsed_response = stk_push_callback_response_parser.parse()

    result = failed_stk_push_callback.get("Body").get("stkCallback")
    description = result.get("ResultDesc")
    result_code = result.get("ResultCode")
    transaction_id = result.get("MerchantRequestID")

    parsed_result = {
        "description": description,
        "success": result_code == 0,
        "transaction_id": transaction_id
    }

    assert f"STK push callback request: {transaction_id} failed. {description}." in caplog.text
    assert parsed_response == parsed_result


def test_stk_push_status_query_response_parser(caplog, failed_stk_push_status_query, successful_stk_push_status_query):
    caplog.set_level(logging.ERROR)
    failed_response = build_response(failed_stk_push_status_query, "utf-8", "OK", 403)

    stk_push_status_query_response_parser = StkPushStatusQueryResponseParser(failed_response)
    parsed_response = stk_push_status_query_response_parser.parse()

    request_id = failed_stk_push_status_query.get("MerchantRequestID")
    description = failed_stk_push_status_query.get("ResultDesc")

    assert f"STK push status query request: {request_id} failed. {description}." in caplog.text
    assert parsed_response == {camel_to_snake(key): value for key, value in failed_stk_push_status_query.items()}

    caplog.set_level(logging.INFO)
    successful_response = build_response(successful_stk_push_status_query, "utf-8", "OK", 200)

    stk_push_status_query_response_parser = StkPushStatusQueryResponseParser(successful_response)
    parsed_response = stk_push_status_query_response_parser.parse()

    request_id = successful_stk_push_status_query.get("MerchantRequestID")
    description = successful_stk_push_status_query.get("ResultDesc")

    assert f"STK push status query request: {request_id} processed successfully. {description}." in caplog.text
    assert parsed_response == {camel_to_snake(key): value for key, value in successful_stk_push_status_query.items()}

