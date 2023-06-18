# standard imports
import os

# external imports
import dotenv
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
env_file = os.path.join(parent_dir, '.env.test')


@pytest.fixture(scope='session')
def load_env_vars():
    dotenv.load_dotenv(dotenv_path=env_file)
