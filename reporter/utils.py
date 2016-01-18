
import re


def get_testcase_id(test_name):
    """Returns test id from name
    For example if test name is "test_ban_l3_agent[once](12345)"
    it returns 12345
    """
    result = re.search(r'\((?P<id>\d{4,})\)', test_name)
    if result is not None:
        return result.group('id')
