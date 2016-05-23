import httpretty
import pytest


@pytest.yield_fixture
def api_mock():
    httpretty.enable()
    httpretty.HTTPretty.allow_net_connect = False
    yield
    httpretty.disable()
    httpretty.reset()
