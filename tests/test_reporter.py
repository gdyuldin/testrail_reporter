import pytest
from reporter import Reporter
from reporter.testrail.client import Case
from reporter.testrail.client import Plan

import six
from six.moves import StringIO

if six.PY2:
    import mock
else:
    from unittest import mock


@pytest.fixture
def reporter():
    reporter = Reporter(iso_link="http://iso_link",
                        xunit_report='tests/xunit_files/report.xml',
                        env_description='vlan_ceph',
                        iso_id=385)
    reporter.config_testrail(
        base_url="https://testrail",
        username="user",
        password="password",
        milestone="0.1",
        project="Test Project",
        tests_suite="Test Suite"
    )
    return reporter


@pytest.mark.parametrize('milestone, iso, name', (
    ('8.0', '123', '8.0 iso #123'),
))
def test_plan_name(reporter, milestone, iso, name):
    reporter.iso_id = iso
    reporter.milestone_name = milestone
    assert reporter.get_plan_name() == name


def test_parse_report(reporter):
    suite, result = reporter.get_xunit_test_suite()
    assert len(list(suite)) == 65
    assert len(result.skipped) == 25
    assert len(result.failures) == 13


def test_print_run_url(reporter, mocker):
    stdout = mocker.patch('sys.stdout', new=StringIO())
    run = mock.Mock(id=2)
    mocker.patch.object(reporter, 'find_testrail_cases', return_value=[Case()])
    mocker.patch.object(reporter, 'get_or_create_plan',
                        return_value=Plan('test_plan'))
    mocker.patch.object(reporter, 'create_test_run', return_value=run)
    reporter.execute()
    assert stdout.getvalue() == (
        '[TestRun URL] https://testrail/index.php?/runs/view/2\n')
