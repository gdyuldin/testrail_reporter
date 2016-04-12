import datetime

import pytest
from testrail_reporter import Reporter
from testrail_reporter.testrail.client import Case
from testrail_reporter.testrail.client import Plan

import six
from six.moves import StringIO

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
    'classname, methodname, job_url, expected_url',
    (('a.b.c.TClass', 'test_method[2](1)', 'http://t_job/',
      'http://t_job/testReport/a.b.c/TClass/test_method_2__1_/'),
     ('a.b.c.TClass', 'test_method[id-1]', 'http://t_job/',
      'http://t_job/testReport/a.b.c/TClass/test_method_id_1_/'),
     ('a.b.c.TClass', 'test_method[a,b]', 'http://t_job/',
      'http://t_job/testReport/a.b.c/TClass/test_method_a_b_/'),
     ('TClass', 'test_method[a,b]', 'http://t_job/',
      'http://t_job/testReport/(root)/TClass/test_method_a_b_/'),
     ('TClass', 'test_method[AS,b]', 'http://t_job/',
      'http://t_job/testReport/(root)/TClass/test_method_AS_b_/'), ))
def test_get_jenkins_report_url(reporter, classname, methodname, job_url,
                                expected_url):
    from testrail_reporter.vendor.xunitparser import TestCase as XunitCase
    xunit_case = XunitCase(classname=classname, methodname=methodname)
    reporter.test_results_link = job_url
    assert expected_url == reporter.get_jenkins_report_url(xunit_case)


def test_add_result_to_case(reporter):
    from testrail_reporter.vendor.xunitparser import TestCase as XunitCase
    testrail_case = Case()
    xunit_case = XunitCase(classname='a.TestClass', methodname='test_method')
    xunit_case.result = 'success'
    xunit_case.message = None
    xunit_case.time = datetime.timedelta(seconds=1)
    report_url = reporter.get_jenkins_report_url(xunit_case)
    reporter.add_result_to_case(testrail_case, xunit_case)
    assert report_url in testrail_case.result.comment
    assert reporter.env_description in testrail_case.result.comment
