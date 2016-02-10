import pytest
import httpretty
import json
import re
from functools import partial

from testrail_reporter.testrail.client import Case
from testrail_reporter.testrail.client import Client
from testrail_reporter.testrail.client import Config
from testrail_reporter.testrail.client import Milestone
from testrail_reporter.testrail.client import Plan
from testrail_reporter.testrail.client import Project
from testrail_reporter.testrail.client import Result
from testrail_reporter.testrail.client import Run
from testrail_reporter.testrail.client import Test as TrTest
from testrail_reporter.testrail.client import Suite


@pytest.yield_fixture
def api_mock():
    httpretty.enable()
    httpretty.HTTPretty.allow_net_connect = False
    yield
    httpretty.disable()
    httpretty.reset()


def _testrail_callback(data_kind):

    project_response = {
        1: {'id': 1}
    }
    suite_response = {
        2: {'id': 2, 'project_id': 1}
    }
    case_response = {
        3: {'id': 3, 'suite_id': 2, 'title': 'case title'},
        31: {'id': 31, 'suite_id': 2, 'title': 'case title31'},
    }
    run_response = {
        4: {'id': 4, 'project_id': 1, 'suite_id': 2, 'milestone_id': 8,
            'config_id': 9}
    }
    result_response = {
        5: {'id': 5, 'status_id': 6}
    }
    status_response = {
        6: {'id': 6, 'name': 'passed'}
    }
    plan_response = {
        7: {'id': 7, 'project_id': 1, 'name': 'old_test_plan'}
    }
    milestone_response = {
        8: {'id': 8, 'project_id': 1}
    }
    config_response = {
        9: {'id': 9, 'project_id': 1}
    }
    test_response = {
        10: {'id': 10, 'run_id': 4}
    }

    def callback(request, uri, headers, _data):
        _id = uri.split('get_{}/'.format(data_kind))[-1]
        print uri, _id
        if _id.isdigit():
            data = _data[int(_id)]
        else:
            data = _data.values()
        return (200, headers, json.dumps(data))

    data = locals().get(data_kind + '_response')

    return partial(callback, _data=data)


@pytest.fixture
def client(api_mock):
    client = Client(
        base_url='http://testrail/',
        username='user',
        password='password')

    base = re.escape(client.base_url)

    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_project(s|/).*'),
        body=_testrail_callback('project'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_suite(s|/).*'),
        body=_testrail_callback('suite'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_case(s|/).*'),
        body=_testrail_callback('case'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_plan(s|/).*'),
        body=_testrail_callback('plan'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_run(s|/).*'),
        body=_testrail_callback('run'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_result(s|/).*'),
        body=_testrail_callback('result'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_status(es|/).*'),
        body=_testrail_callback('status'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_milestone(s|/).*'),
        body=_testrail_callback('milestone'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_config(s|/).*'),
        body=_testrail_callback('config'),
        match_querystring=True)
    httpretty.register_uri(
        httpretty.GET,
        re.compile(base + r'get_test(s|/).*'),
        body=_testrail_callback('test'),
        match_querystring=True)
    return client


@pytest.fixture
def project(client):
    projects = client.projects()
    return projects[0]


@pytest.fixture
def suite(project):
    suites = project.suites()
    return suites[0]


@pytest.fixture
def case(suite):
    cases = suite.cases()
    return cases[0]


@pytest.fixture
def run(project):
    runs = project.runs()
    return runs[0]


@pytest.fixture
def test(run):
    tests = run.tests()
    return tests[0]


@pytest.fixture
def milestone(project):
    milestones = project.milestones()
    return milestones[0]


@pytest.fixture
def plan(project):
    plans = project.plans()
    return plans[0]


@pytest.fixture
def config(project):
    configs = project.configs()
    return configs[0]


def test_projects(client):
    projects = client.projects()
    assert isinstance(projects, list)
    assert isinstance(projects[0], Project)


def test_project(client, project):
    fetched_project = client.projects(id=project.id)
    assert fetched_project.id == project.id


def test_get_project(client, project):
    fetched_project = client.projects.get(project.id)
    assert fetched_project.id == project.id


def test_suites(project):
    suites = project.suites()
    assert isinstance(suites, list)
    assert isinstance(suites[0], Suite)
    assert suites[0].project_id == project.id


def test_suite(project, suite):
    fetched_suite = project.suites(id=suite.id)
    assert fetched_suite.id == suite.id


def test_cases(suite):
    cases = suite.cases()
    assert isinstance(cases, list)
    assert isinstance(cases[0], Case)
    assert cases[0].suite_id == suite.id


def test_case(suite, case):
    fetched_case = suite.cases(id=case.id)
    assert fetched_case.id == case.id


def test_runs(project):
    runs = project.runs()
    assert isinstance(runs, list)
    assert isinstance(runs[0], Run)
    assert runs[0].project_id == project.id


def test_run(project, run):
    fetched_run = project.runs(id=run.id)
    assert fetched_run.id == run.id


def test_tr_tests(run):
    tests = run.tests()
    assert isinstance(tests, list)
    assert isinstance(tests[0], TrTest)
    assert tests[0].run_id == run.id


def test_tr_test(run, test):
    fetched_test = run.tests(id=test.id)
    assert fetched_test.id == test.id


def test_results(run):
    results = run.results()
    assert isinstance(results, list)
    assert isinstance(results[0], Result)


def test_statuses(client):
    statuses = client.statuses
    assert type(statuses) is dict
    assert 'passed' in statuses.values()


def test_plans(project):
    plans = project.plans()
    assert isinstance(plans, list)
    assert isinstance(plans[0], Plan)
    assert plans[0].project_id == project.id


def test_plan(project, plan):
    fetched_plan = project.plans(id=plan.id)
    assert fetched_plan.id == plan.id


def test_configs(project):
    configs = project.configs()
    assert isinstance(configs, list)
    assert isinstance(configs[0], Config)
    assert configs[0].project_id == project.id


def test_config(project, config):
    fetched_config = project.configs(id=config.id)
    assert fetched_config.id == config.id


def test_milestones(project):
    milestones = project.milestones()
    assert isinstance(milestones, list)
    assert isinstance(milestones[0], Milestone)
    assert milestones[0].project_id == project.id


def test_milestone(project, milestone):
    fetched_milestone = project.milestones(id=milestone.id)
    assert fetched_milestone.id == milestone.id


def test_find(suite):
    case = suite.cases.find(title='case title')
    assert type(case) is Case
    assert case.title == 'case title'


def test_unsuccess_find(suite):
    case = suite.cases.find(title='case title1')
    assert case is None


def test_add_plan(client, project):
    base = re.escape(client.base_url)

    httpretty.register_uri(
        httpretty.POST,
        re.compile(base + r'add_plan/.*'),
        body=json.dumps({'id': 8, 'project_id': 1, 'name': 'old_test_plan'}),
        match_querystring=True)
    new_plan = project.plans.add(name='test_plan', milestone_id=7)
    expected = {
        "milestone_id": 7,
        "entries": [],
        "description": None,
        "name": "test_plan"
    }
    result = json.loads(httpretty.last_request().body)
    assert expected == result
    assert type(new_plan) is Plan
    assert new_plan.id == 8


def test_add_run_to_plan(client, plan):
    base = re.escape(client.base_url)

    httpretty.register_uri(
        httpretty.POST,
        re.compile(base + r'add_plan_entry/.*'),
        body=json.dumps({'runs': [{'id': 8}]}),
        match_querystring=True)

    run = Run(suite_id=14, milestone_id=15, name="test_run",
        description="test description", case_ids=[1, 2], config_ids=[16])
    plan.add_run(run)
    expected = {
        "suite_id": 14,
        "name": "test_run",
        "description": "test description",
        "include_all": False,
        "case_ids": [1, 2],
        "config_ids": [16],
        "runs": [
            {
                "name": "test_run",
                "description": "test description",
                "case_ids": [1, 2],
                "config_ids": [16]
            }
        ]
    }
    result = json.loads(httpretty.last_request().body)
    assert expected == result
    assert run.id == 8


def test_add_result(client, run):
    base = re.escape(client.base_url)

    httpretty.register_uri(
        httpretty.POST,
        re.compile(base + r'add_result/.*'),
        body=json.dumps({'id': 5, 'status_id': 4}),
        match_querystring=True)
    result = run.results.add(status_id=1, comment="test result comment")
    expected = {
        "assignedto_id": None,
        "comment": "test result comment",
        "defects": None,
        "elapsed": None,
        "status_id": 1,
        "version": None,
    }
    request = json.loads(httpretty.last_request().body)
    assert request == expected
    assert type(result) is Result
    assert result.id == 5


def test_add_result_to_case():
    pass


def test_add_results_for_cases(client, suite, run):
    base = re.escape(client.base_url)

    httpretty.register_uri(
        httpretty.POST,
        re.compile(base + r'add_results_for_cases/.*'),
        body=json.dumps([{'id': 5, 'status_id': 4}]),
        match_querystring=True)
    cases = suite.cases()
    for case in cases[:-1]:
        case.add_result(status_id=1, comment="test result comment")
    new_results = run.add_results_for_cases(cases)
    expected = {
        "results": [
            {
                "case_id": 3,
                "assignedto_id": None,
                "comment": "test result comment",
                "defects": None,
                "elapsed": None,
                "status_id": 1,
                "version": None,
            },
        ]
    }
    result = json.loads(httpretty.last_request().body)
    assert expected == result
    assert type(new_results) is list
    assert type(new_results[0]) is Result
    assert new_results[0].id == 5


@pytest.mark.parametrize('statuses', (
    [200],
    [429, 200],
    [429, 429, 429, 429, 200],
    pytest.mark.xfail([429, 429, 429, 429, 429, 200]),
    pytest.mark.xfail([300]),
    pytest.mark.xfail([400]),
    pytest.mark.xfail([500]),
))
def test_http_errors(api_mock, mocker, statuses):
    client = Client(
        base_url='http://testrail/',
        username='user',
        password='password')

    def request_callback(request, uri, headers):
        status = statuses.pop(0)
        return (status, headers, "[]")

    url = re.escape('http://testrail/index.php?/api/v2/get_projects')

    httpretty.register_uri(
        httpretty.GET,
        re.compile(url),
        body=request_callback,
        match_querystring=True)

    mocker.patch('time.sleep')
    client.projects()
