import pytest
from reporter import Reporter


@pytest.fixture
def reporter():
    return Reporter(iso_link="http://iso_link",
                    xunit_report='tests/xunit_files/report.xml',
                    env_description='vlan_ceph',
                    iso_id=385)


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
