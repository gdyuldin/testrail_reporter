import requests_mock
import pytest

import testrail


@pytest.yield_fixture
def api_mock():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def testrail_client_mock(mocker):
    project = testrail.project.Project()
    mocker.patch('testrail.TestRail.project', return_value=project)
    statuses = [
        testrail.status.Status({
            'name': 'passed'
        }),
        testrail.status.Status({
            'name': 'failed'
        }),
        testrail.status.Status({
            'name': 'skipped'
        }),
        testrail.status.Status({
            'name': 'blocked'
        }),
    ]
    mocker.patch('testrail.TestRail.statuses', return_value=statuses)
    return
