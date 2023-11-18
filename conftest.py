# This file needs to be here so I can run pytest from the root directory
# I do not know why, but it was the solution that worked from:
# https://stackoverflow.com/questions/20985157/py-test-no-module-named
import pytest
import time
from main import app

@pytest.fixture()
def the_app():
    yield app

@pytest.fixture()
def client(the_app):
    return the_app.test_client()

# Add a sleep between tests so we don't hit the rate limiter unintentionally
@pytest.fixture(autouse=True)
def delay_tests():
    yield
    time.sleep(3)