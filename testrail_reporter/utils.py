
import re
from uuid import UUID


def get_testcase_id(test_name):
    """Returns test id from name
    For example if test name is "test_ban_l3_agent[once](12345)"
    it returns 12345

    Matching variants:
        * test_ban_l3_agent[once](12345)
        * test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb]
    """
    # name like "test_ban_l3_agent[once](12345)"
    result = re.search(r'\((?P<id>\d{4,})\)', test_name)
    if result is not None:
        return result.group('id')
    # name like "test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb]"
    result = re.search(r'\[id-(?P<id>.+)\]', test_name)
    if result is not None:
        try:
            uuid = UUID(hex=result.group('id'))
            return str(uuid)
        except ValueError:
            pass
