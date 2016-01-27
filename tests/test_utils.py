import pytest

from testrail_reporter.utils import get_testcase_id


@pytest.mark.parametrize('case_name, expected_id', (
    ('test_ban_l3_agent[once][(12345)]', '12345'),
    ('test_ban_l3_agent_54321[once][(12345)]', '12345'),
    ('12345_test_ban_l3_agent[once]', None),
    ('test_ban_l3_agent_123', None),
    ('test_ban_l3_agent_12345', None),
    (
        'test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb]',
        '2390f766-836d-40ef-9aeb-e810d78207fb'
    ),
    (
        'test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb,network]',
        '2390f766-836d-40ef-9aeb-e810d78207fb'
    ),
    (
        'test_quotas[network,id-2390f766-836d-40ef-9aeb-e810d78207fb,network]',
        '2390f766-836d-40ef-9aeb-e810d78207fb'
    ),
    (
        'test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fg]', None
    ),
    (
        'test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207f]', None
    ),
))
def test_extract_case_id(case_name, expected_id):
    assert get_testcase_id(case_name) == expected_id
