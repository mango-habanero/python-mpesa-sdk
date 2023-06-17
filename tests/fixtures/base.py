import os

import dotenv
import pytest

@pytest.fixture(scope='session')
def load_env_vars():
    dotenv.load_dotenv()
