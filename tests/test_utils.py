# standard imports
import logging

# external imports
import pytest
import requests_mock
from mpesa_sdk.exceptions import UnsupportedMethodError
from requests import Response

# local imports
from mpesa_sdk.utils import make_request, preprocess_http_response

# test imports
from tests.helpers.http import build_response


def test_make_request(caplog):
    sample_url = "http://some-url.example"
    with pytest.raises(UnsupportedMethodError):
        make_request("SAMPLE", sample_url)

    caplog.set_level(logging.DEBUG)
    sample_data = {"foo": "bar"}
    with requests_mock.Mocker(real_http=False) as mock_request:
        mock_request.request("PUT", sample_url)
        make_request("PUT", sample_url, data=sample_data)
    assert f'Putting to: {sample_url} with: {sample_data}.' in caplog.text


def reason_status_code(response: Response) -> tuple:
    return response.reason, response.status_code


def test_preprocess_http_response(caplog):
    caplog.set_level(logging.ERROR)
    info_errors_response = build_response(None, "utf-8", "Switching Protocols", 101)
    reason, status_code = reason_status_code(info_errors_response)
    data = preprocess_http_response(info_errors_response)
    assert f'Informational errors: {status_code}, reason: {reason}.' in caplog.text
    assert data is None

    caplog.set_level(logging.INFO)
    sample_content = {
        "foo": "bar"
    }
    successful_response = build_response(sample_content, "utf-8", "OK", 200)
    data = preprocess_http_response(successful_response)
    assert 'Request was successful, returning response.' in caplog.text
    assert data == sample_content

    caplog.set_level(logging.ERROR)
    redirect_errors_response = build_response(None, "utf-8", "Not Modified", 304)
    reason, status_code = reason_status_code(redirect_errors_response)
    data = preprocess_http_response(redirect_errors_response)
    assert f'Redirect Issues: {status_code}, reason: {reason}.' in caplog.text
    assert data is None

    client_errors_response = build_response(None, "utf-8", "Not Found", 404)
    reason, status_code = reason_status_code(client_errors_response)
    data = preprocess_http_response(client_errors_response)
    assert f'Client Error: {status_code}, reason: {reason}.' in caplog.text
    assert data is None

    server_errors_response = build_response(None, "utf-8", "Bad Gateway", 502)
    reason, status_code = reason_status_code(server_errors_response)
    data = preprocess_http_response(server_errors_response)
    assert f'Server Error: {status_code}, reason: {reason}.' in caplog.text
    assert data is None

