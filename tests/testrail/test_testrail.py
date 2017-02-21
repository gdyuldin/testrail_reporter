import pytest
import json
import re
from functools import partial

from xunit2testrail.testrail.client import Case
from xunit2testrail.testrail.client import Client
from xunit2testrail.testrail.client import Config
from xunit2testrail.testrail.client import Milestone
from xunit2testrail.testrail.client import Plan
from xunit2testrail.testrail.client import Project
from xunit2testrail.testrail.client import Result
from xunit2testrail.testrail.client import Run
from xunit2testrail.testrail.client import Test as TrTest
from xunit2testrail.testrail.client import Suite
from xunit2testrail.testrail.exceptions import NotFound


def _testrail_callback(data_kind):

    project_response = {1: {'id': 1}}
    suite_response = {2: {'id': 2, 'project_id': 1}}
    case_response = {
        3: {
            'id': 3,
            'suite_id': 2,
            'title': 'case title'
        },
        31: {
            'id': 31,
            'suite_id': 2,
            'title': 'case title31'
        },
    }
    run_response = {
        4: {
            'id': 4,
            'project_id': 1,
            'suite_id': 2,
            'milestone_id': 8,
            'config_ids': [9],
            'plan_id': None,
        },
        13: {
            'id': 13,
            'project_id': 1,
            'suite_id': 2,
            'milestone_id': 8,
            'config_ids': [9],
            'plan_id': 8,
            'name': 'some test run',
            'description': None,
            'assignedto_id': None,
            'case_ids': []
        },
    }
    result_response = {5: {'id': 5, 'status_id': 6}}
    status_response = {6: {'id': 6, 'name': 'passed'}}
    plan_response = {7: {'id': 7, 'project_id': 1, 'name': 'old_test_plan'},
                     8: {'id': 8, 'project_id': 1, 'name': 'new_test_plan',
                         'entries': [{'runs': [{'id': 13,
                                                'name': 'some test run'}],
                                      'id': 12}]}}
    milestone_response = {8: {'id': 8, 'project_id': 1}}
    config_response = {9: {'id': 9, 'project_id': 1}}
    test_response = {10: {'id': 10, 'run_id': 4, 'case_id': 5}}

    def callback(request, context, _data):
        context.status_code = 200
        _id = request.query.split('get_{}/'.format(data_kind))[-1]
        if _id.isdigit():
            data = _data[int(_id)]
        else:
            data = list(_data.values())
        return json.dumps(data)

    data = locals().get(data_kind + '_response')

    return partial(callback, _data=data)


@pytest.fixture
def client(api_mock):
    client = Client(
        base_url='http://testrail/', username='user', password='password')

    base = re.escape(client.base_url)

    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_project(s|/).*'),
        text=_testrail_callback('project'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_suite(s|/).*'),
        text=_testrail_callback('suite'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_case(s|/).*'),
        text=_testrail_callback('case'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_plan(s|/).*'),
        text=_testrail_callback('plan'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_run(s|/).*'),
        text=_testrail_callback('run'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_result(s|/).*'),
        text=_testrail_callback('result'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_status(es|/).*'),
        text=_testrail_callback('status'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_milestone(s|/).*'),
        text=_testrail_callback('milestone'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_config(s|/).*'),
        text=_testrail_callback('config'),
        complete_qs=True)
    api_mock.register_uri(
        'GET',
        re.compile(base + r'get_test(s|/).*'),
        text=_testrail_callback('test'),
        complete_qs=True)
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
    assert tests[0].case_id == 5


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


def test_find_run_in_plan(project):
    plan = project.plans.find(name='new_test_plan')
    assert type(plan) is Plan
    assert plan.name == 'new_test_plan'
    assert plan.entries[0]['id'] == 12
    included_run = plan.runs.find(name='some test run')
    assert type(included_run) is Run
    assert included_run.id == 13
    assert included_run.plan_id == 8


def test_unsuccess_find(suite):
    with pytest.raises(NotFound):
        suite.cases.find(title='case title1')


def test_list(project):
    runs = project.runs.list()
    assert len(runs) == 2
    first_run = runs.find(config_ids=[9], suite_id=2)
    assert type(first_run) == Run
    assert first_run.id == 4


def test_add_plan(api_mock, client, project):
    base = re.escape(client.base_url)

    api_mock.register_uri(
        'POST',
        re.compile(base + r'add_plan/.*'),
        json={'id': 8,
              'project_id': 1,
              'name': 'old_test_plan'},
        complete_qs=True)
    new_plan = project.plans.add(name='test_plan', milestone_id=7)
    expected = {
        "milestone_id": 7,
        "entries": [],
        "description": None,
        "name": "test_plan"
    }
    result = api_mock.request_history[-1].json()
    assert expected == result
    assert type(new_plan) is Plan
    assert new_plan.id == 8


def test_add_run_to_plan(api_mock, client, plan):
    base = re.escape(client.base_url)

    api_mock.register_uri(
        'POST',
        re.compile(base + r'add_plan_entry/.*'),
        json={'runs': [{
            'id': 8
        }]},
        complete_qs=True)

    run = Run(suite_id=14,
              milestone_id=15,
              name="test_run",
              description="test description",
              case_ids=[1, 2],
              config_ids=[16])
    plan.add_run(run)
    expected = {
        "suite_id": 14,
        "name": "test_run",
        "description": "test description",
        "include_all": False,
        "case_ids": [1, 2],
        "config_ids": [16],
        "runs": [{
            "name": "test_run",
            "description": "test description",
            "case_ids": [1, 2],
            "config_ids": [16]
        }]
    }
    result = api_mock.request_history[-1].json()
    assert expected == result
    assert run.id == 8


def test_update_run_in_plan(api_mock, client, project, plan):
    base = re.escape(client.base_url)

    api_mock.register_uri(
        'POST',
        re.compile(base + 'update_plan_entry/{0}/.*'.format(plan.id)),
        json={'runs': [{
            'id': 13,
            'case_ids': [10, 20, 30]
        }]},
        complete_qs=True)

    run_to_update = project.runs.find(plan_id=plan.id)
    run_to_update.case_ids = [10, 20, 30]

    plan.update_run(run_to_update)
    expected = {
        "suite_id": run_to_update.suite_id,
        "name": run_to_update.name,
        "description": run_to_update.description,
        "include_all": False,
        "case_ids": run_to_update.case_ids,
        "config_ids": run_to_update.config_ids,
        "milestone_id": run_to_update.milestone_id,
        "project_id": run_to_update.project_id,
        "assignedto_id": run_to_update.assignedto_id,
        "plan_id": run_to_update.plan_id,
    }
    result = api_mock.request_history[-1].json()

    assert expected == result
    assert plan.entries[0]['runs'][0]['case_ids'] == [10, 20, 30]


def test_add_result(api_mock, client, run):
    base = re.escape(client.base_url)

    api_mock.register_uri(
        'POST',
        re.compile(base + r'add_result/.*'),
        json={'id': 5,
              'status_id': 4},
        complete_qs=True)
    result = run.results.add(status_id=1, comment="test result comment")
    expected = {
        "assignedto_id": None,
        "comment": "test result comment",
        "defects": None,
        "elapsed": None,
        "status_id": 1,
        "version": None,
    }
    request = api_mock.request_history[-1].json()
    assert request == expected
    assert type(result) is Result
    assert result.id == 5


def test_add_case(api_mock, client, suite):
    base = re.escape(client.base_url)

    api_mock.register_uri(
        'POST',
        re.compile(base + r'add_case/157'),
        json={'id': 8,
              'project_id': 1,
              'title': 'case'},
        complete_qs=True)
    new_case = suite.cases.add(title='test_case',
                               milestone_id=7,
                               description='test_case_description',
                               section_id=157)
    expected = {
        "milestone_id": 7,
        "description": 'test_case_description',
        "title": "test_case"
    }
    result = api_mock.request_history[-1].json()
    assert expected == result
    assert type(new_case) is Case
    assert new_case.id == 8


def test_add_results_for_cases(api_mock, client, suite, run):
    base = re.escape(client.base_url)

    api_mock.register_uri(
        'POST',
        re.compile(base + r'update_run/.*'),
        json={'id': 4},
        complete_qs=True)
    api_mock.register_uri(
        'POST',
        re.compile(base + r'add_results_for_cases/.*'),
        json=[{
            'id': 5,
            'status_id': 4
        }],
        complete_qs=True)
    cases = suite.cases()
    for case in cases[:-1]:
        case.add_result(status_id=1, comment="test result comment")
    new_results = run.add_results_for_cases(cases)
    expected = {
        "results": [{
            "case_id": 3,
            "assignedto_id": None,
            "comment": "test result comment",
            "defects": None,
            "elapsed": None,
            "status_id": 1,
            "version": None,
        }, ]
    }
    result = api_mock.request_history[-1].json()
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
    pytest.mark.xfail([500]), ))
def test_http_errors(api_mock, mocker, statuses):
    client = Client(
        base_url='http://testrail/', username='user', password='password')

    def request_callback(request, context):
        status = statuses.pop(0)
        context.status_code = status
        return "[]"

    url = re.escape('http://testrail/index.php?/api/v2/get_projects')

    api_mock.register_uri(
        'GET', re.compile(url), text=request_callback, complete_qs=True)

    mocker.patch('time.sleep')
    client.projects()
