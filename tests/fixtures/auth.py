# standard imports
import os
import logging

# external imports
import pytest

# local imports

logg = logging.getLogger(__file__)


@pytest.fixture(scope='function')
def successful_oauth_response():
    return {
        "access_token": "FF6C9WiPk46ShjYk2QqWajV95VaN",
        "expires_in": "3599"
    }


@pytest.fixture(scope="function")
def failed_oauth_response():
    return {
        "requestId": "98947-26371777-2",
        "errorCode": "400.008.01",
        "errorMessage": "Invalid Authentication passed"
    }