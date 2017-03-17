# -*- coding: utf-8 -*-
import datetime
import re

import pytest
import six
from six.moves import StringIO
import testrail

from xunit2testrail import Reporter

if six.PY2:
    import mock
else:
    from unittest import mock


@pytest.fixture
def reporter(testrail_client_mock):
    reporter = Reporter(
        env_description='vlan_ceph',
        test_results_link="http://test_job/",
        case_mapper=None,
        paste_url='http://example.com/')
    reporter.config_testrail(
        base_url="https://testrail",
        username="user",
        password="password",
        milestone="0.1",
        project="Test Project",
        tests_suite="Test Suite",
        plan_name="Plan name")
    return reporter


@pytest.fixture
def xunit_case():
    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase
    xunit_case = XunitCase(classname='a.TestClass', methodname='test_method')
    xunit_case.result = 'success'
    xunit_case.time = datetime.timedelta(seconds=1)
    return xunit_case


@pytest.fixture
def xunit_case_skipped(xunit_case):
    xunit_case.result = 'skipped'
    return xunit_case


@pytest.fixture
def paste_api(api_mock):
    paste_url = re.escape('http://example.com/json/?method=pastes.newPaste')
    api_mock.register_uri(
        'POST', re.compile(paste_url), json={"data": "123"}, complete_qs=True)


def test_print_run_url(reporter, mocker):
    stdout = mocker.patch('sys.stdout', new=StringIO())
    reporter.print_run_url(mock.Mock(url='http://report_url/'))
    assert stdout.getvalue() == ('[TestRun URL] http://report_url/\n')


@pytest.mark.parametrize('classname, methodname, expected_url', (
    ('a.b.c.TClass', 'test_method[2](1)',
     'http://t_job/testReport/a.b.c/TClass/test_method_2__1_/'),
    ('a.b.c.TClass', 'test_method[id-1]',
     'http://t_job/testReport/a.b.c/TClass/test_method_id_1_/'),
    ('a.b.c.TClass', 'test_method[a,b]',
     'http://t_job/testReport/a.b.c/TClass/test_method_a_b_/'),
    ('TClass', 'test_method[a,b]',
     'http://t_job/testReport/(root)/TClass/test_method_a_b_/'),
    ('TClass', 'test_method[AS,b]',
     'http://t_job/testReport/(root)/TClass/test_method_AS_b_/'), ))
def test_get_jenkins_report_url(reporter, classname, methodname, expected_url):

    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase
    xunit_case = XunitCase(classname=classname, methodname=methodname)
    reporter.test_results_link = 'http://t_job/'
    assert expected_url == reporter.get_jenkins_report_url(xunit_case)


def test_get_cases_results_data_comment(reporter, xunit_case):
    xunit_case.message = u'успешно'
    xunit_case.stderr = u'stderr message сообщение'
    xunit_case.stdout = u'stdout message сообщение'
    xunit_case.trace = u'trace сообщение'
    report_url = reporter.get_jenkins_report_url(xunit_case)
    result_data = reporter.get_cases_results_data(xunit_case)
    comment = result_data['comment']
    assert report_url in comment
    assert reporter.env_description in comment
    assert xunit_case.message in comment
    assert xunit_case.stderr not in comment
    assert xunit_case.stdout not in comment
    assert xunit_case.trace in comment


@pytest.mark.parametrize(['xunit_status', 'testrail_status'], [
    ('success', 'passed'),
    ('failure', 'failed'),
    ('error', 'blocked'),
    ('skipped', 'skipped'),
])
def test_get_cases_results_data_status(reporter, xunit_case, xunit_status,
                                       testrail_status):
    xunit_case.result = xunit_status
    reporter.send_skipped = True
    result_data = reporter.get_cases_results_data(xunit_case)
    assert result_data['status'].name == testrail_status


@pytest.mark.parametrize('send_skipped', [True, False])
def test_send_skipped_param(reporter, xunit_case_skipped, send_skipped):
    reporter.send_skipped = send_skipped
    result_data = reporter.get_cases_results_data(xunit_case_skipped)
    assert send_skipped == (result_data is not None)


def test_no_trace_on_success_test_on_testrail(reporter, xunit_case):
    assert 'trace' not in reporter.gen_testrail_comment(xunit_case)


def test_paste_result_link(reporter, xunit_case, paste_api):
    link = reporter.save_to_paste(xunit_case)
    assert link == "http://example.com/show/123/"


@pytest.mark.parametrize('prop, value', (
    ('trace', "i'm trace"),
    ('stdout', "i'm stdout"),
    ('stderr', "i'm stderr"), ))
def test_paste_store_data(api_mock, reporter, xunit_case, paste_api, prop,
                          value):
    absent_props = ['trace', 'stdout', 'stderr']
    absent_props.remove(prop)
    setattr(xunit_case, prop, value)
    reporter.save_to_paste(xunit_case)
    payload = api_mock.request_history[-1].json()
    assert value in payload['code']
    for absent_prop in absent_props:
        assert absent_prop not in payload['code']


def test_get_plan(reporter, mocker):
    expected_plan = mock.Mock()
    mocker.patch('testrail.TestRail.plan', return_value=expected_plan)
    plan = reporter.get_or_create_plan()
    assert plan == expected_plan


def test_create_plan(reporter, mocker):
    expected_plan = mock.Mock()
    saved_plan = mock.Mock()
    mocker.patch('testrail.TestRail.milestone')
    add_method = mocker.patch('testrail.TestRail.add', return_value=saved_plan)
    mocker.patch('testrail.TestRail.plan', side_effect=[None, expected_plan])
    plan = reporter.get_or_create_plan()
    assert plan == saved_plan
    add_method.assert_called_once_with(expected_plan)


def test_get_exists_test_run(reporter, mocker):
    entry_name = ("{0.env_description} "
                  "<{0.tests_suite_name}>").format(reporter).strip()
    expected_run = mock.Mock()
    mocker.patch(
        'testrail.entry.Entry.runs',
        new_callable=mock.PropertyMock,
        return_value=[expected_run])
    entry = testrail.entry.Entry({'name': entry_name})
    mocker.patch(
        'testrail.plan.Plan.entries',
        new_callable=mock.PropertyMock,
        return_value=[entry])
    plan = testrail.plan.Plan({'id': 1, 'name': 'plan'})
    reporter.use_test_run_if_exists = True
    run = reporter.get_or_create_test_run(plan, {})
    assert run == expected_run


def test_get_not_exists_test_run(reporter, mocker):
    expected_run = mock.Mock()
    saved_run = mock.Mock()
    mocker.patch(
        'testrail.plan.Plan.entries',
        new_callable=mock.PropertyMock,
        return_value=[])
    plan = testrail.plan.Plan({'id': 1, 'name': 'plan'})
    mocker.patch('testrail.TestRail.milestone')
    mocker.patch('testrail.TestRail.suite')
    mocker.patch('testrail.TestRail.run', return_value=expected_run)
    add_method = mocker.patch('testrail.TestRail.add', return_value=saved_run)
    reporter.use_test_run_if_exists = True
    run = reporter.get_or_create_test_run(plan, {})
    assert run == saved_run
    add_method.assert_called_once_with(expected_run)


def test_create_test_run(reporter, mocker):
    expected_run = mock.Mock()
    saved_run = mock.Mock()
    plan = testrail.plan.Plan({'name': 'plan', 'id': 1})
    mocker.patch('testrail.TestRail.milestone')
    mocker.patch('testrail.TestRail.suite')
    mocker.patch('testrail.TestRail.run', return_value=expected_run)
    add_method = mocker.patch('testrail.TestRail.add', return_value=saved_run)
    run = reporter.get_or_create_test_run(plan, {})
    assert run == saved_run
    add_method.assert_called_once_with(expected_run)
