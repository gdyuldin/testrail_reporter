import requests_mock
import pytest


@pytest.yield_fixture
def api_mock():
    with requests_mock.Mocker() as m:
        yield m
