# -*- coding: utf-8 -*-
import datetime

import pytest
import six
from six.moves import StringIO

from testrail_reporter import Reporter
from testrail_reporter.testrail.client import Case
from testrail_reporter.testrail.client import Plan

if six.PY2:
    import mock
else:
    from unittest import mock


@pytest.fixture
def testrail_client(mocker):
    fake_statuses = mock.PropertyMock(return_value={1: 'passed'})
    mocker.patch('testrail_reporter.reporter.TrClient.statuses',
                 new_callable=fake_statuses)
    return


@pytest.fixture
def reporter(testrail_client):
    reporter = Reporter(xunit_report='tests/xunit_files/report.xml',
                        env_description='vlan_ceph',
                        test_results_link="http://test_job/",
                        case_mapper=None)
    reporter.config_testrail(base_url="https://testrail",
                             username="user",
                             password="password",
                             milestone="0.1",
                             project="Test Project",
                             tests_suite="Test Suite",
                             plan_name="Plan name")
    return reporter


@pytest.fixture
def xunit_case():
    from testrail_reporter.vendor.xunitparser import TestCase as XunitCase
    xunit_case = XunitCase(classname='a.TestClass', methodname='test_method')
    xunit_case.result = 'success'
    xunit_case.time = datetime.timedelta(seconds=1)
    return xunit_case


def test_parse_report(reporter):
    suite, result = reporter.get_xunit_test_suite()
    assert len(list(suite)) == 65
    assert len(result.skipped) == 25
    assert len(result.failures) == 13


def test_print_run_url(reporter, mocker):
    stdout = mocker.patch('sys.stdout', new=StringIO())
    run = mock.Mock(url='http://report_url/')
    mocker.patch.object(reporter, 'find_testrail_cases', return_value=[Case()])
    mocker.patch.object(reporter,
                        'get_or_create_plan',
                        return_value=Plan('test_plan'))
    mocker.patch.object(reporter, 'create_test_run', return_value=run)
    reporter.execute()
    assert stdout.getvalue() == ('[TestRun URL] http://report_url/\n')


@pytest.mark.parametrize(
    'classname, methodname, expected_url',
    (('a.b.c.TClass', 'test_method[2](1)',
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

    from testrail_reporter.vendor.xunitparser import TestCase as XunitCase
    xunit_case = XunitCase(classname=classname, methodname=methodname)
    reporter.test_results_link = 'http://t_job/'
    assert expected_url == reporter.get_jenkins_report_url(xunit_case)


def test_add_result_to_case(reporter, xunit_case):
    testrail_case = Case()
    xunit_case.message = u'успешно'
    xunit_case.stderr = u'stderr message сообщение'
    xunit_case.stdout = u'stdout message сообщение'
    xunit_case.trace = u'trace сообщение'
    report_url = reporter.get_jenkins_report_url(xunit_case)
    reporter.add_result_to_case(testrail_case, xunit_case)
    comment = testrail_case.result.comment
    assert report_url in comment
    assert reporter.env_description in comment
    assert xunit_case.message in comment
    assert xunit_case.stderr not in comment
    assert xunit_case.stdout not in comment
    assert xunit_case.trace in comment


def test_no_trace_on_success_test_on_testrail(reporter, xunit_case):
    assert 'trace' not in reporter.gen_testrail_comment(xunit_case)
