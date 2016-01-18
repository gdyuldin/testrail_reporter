import pytest

from reporter.utils import get_testcase_id


@pytest.mark.parametrize('case_name, expected_id', (
    ('test_ban_l3_agent[once](12345)', '12345'),
    ('test_ban_l3_agent(12)[once](12345)', '12345'),
    ('(12345)test_ban_l3_agent[once]', '12345'),
    ('test_ban_l3_agent(123)', None),
    ('test_ban_l3_agent_12345', None),
))
def test_extract_case_id(case_name, expected_id):
    assert get_testcase_id(case_name) == expected_id
