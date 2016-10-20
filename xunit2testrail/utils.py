import re
from uuid import UUID
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def find_id(methodname):
    """Returns test id from name
    For example if test name is "test_ban_l3_agent[once][(12345)]"
    it returns 12345
    """
    result = re.search(r'\((?P<id>\d{4,})\)', methodname)
    if result is not None:
        return result.group('id')


def find_uuid(methodname):
    """Returns uuid from test methodname (if exists)
    For example if test name is
        "test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb,network]"
    it returns 2390f766-836d-40ef-9aeb-e810d78207fb

    Matching variants:
        * test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb]
        * test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb,network]
    """
    result = re.search(r'\[(?:.*,)?id-(?P<id>.+?)(?:,.+)?\]', methodname)
    if result is not None:
        try:
            uuid = UUID(hex=result.group('id'))
            return str(uuid)
        except ValueError:
            pass


def describe_xunit_case(case):
    return {
        'classname': case.classname,
        'methodname': case.methodname,
        'id': find_id(case.methodname),
        'uuid': find_uuid(case.methodname)
    }


class CaseMapper(object):
    def __init__(self, xunit_name_template, testrail_name_template):
        self.xunit_name_template = xunit_name_template
        self.testrail_name_template = testrail_name_template

    def get_suitable_cases(self, xunit_case, cases):
        xunit_dict = describe_xunit_case(xunit_case)
        xunit_id = self.xunit_name_template.format(**xunit_dict)
        if 'None' in xunit_id:
            logger.warning("Can't extract {template} from {case}".format(
                template=self.xunit_name_template, case=xunit_case))
            return []

        # Search symbols groups, which is absent in xunit_id
        split_symbols_base = [r'a-zA-Z', r'\(\)', r'\[\]', r',', ]
        split_symbols = ''
        for group in split_symbols_base:
            if re.search(r'[{}]'.format(group), xunit_id) is None:
                split_symbols += group
        split_expr = re.compile(r'[{}]'.format(split_symbols))
        match_cases = []
        for case in cases:
            testrail_id = self.testrail_name_template.decode(
                'utf-8').format(**case.data).encode('utf-8')
            groups = [x for x in split_expr.split(testrail_id) if x]
            groups.reverse()
            for group in groups:
                if group == xunit_id:
                    match_cases.append(case)
        return match_cases

    def map(self, xunit_suite, testrail_cases):
        def get_duplicates(array, pos):
            grouped = defaultdict(list)
            for el in array:
                el = list(el)
                index = el.pop(pos)
                grouped[index].append(el[0])
            return [(k, v) for k, v in grouped.items() if len(v) > 1]

        mapping = []
        for xunit_case in xunit_suite:
            suitable_cases = self.get_suitable_cases(xunit_case,
                                                     testrail_cases)
            if len(suitable_cases) == 0:
                logger.warning(
                    "xUnit case {0.classname}.{0.methodname} doesn't match "
                    "any TestRail Case".format(xunit_case))
            for testrail_case in suitable_cases:
                mapping.append((testrail_case, xunit_case))

        duplicated_xunit_cases = get_duplicates(mapping, 0)
        if duplicated_xunit_cases:
            logger.error('Found xunit cases matches to single testrail case:')
            for tr_case, xu_cases in duplicated_xunit_cases:
                for xu_case in xu_cases:
                    logger.error('TestRail "{0.title}" - xUnit "{1.classname}.'
                                 '{1.methodname}"'.format(tr_case, xu_case))
            raise Exception("Can't map some xunit cases")
        duplicated_testrail_cases = get_duplicates(mapping, 1)
        if duplicated_testrail_cases:
            logger.error('Found testrail cases matches to single xunit case:')
            for xu_case, tr_cases in duplicated_testrail_cases:
                for tr_case in tr_cases:
                    logger.error('xUnit "{1.classname}.{1.methodname} - '
                                 'TestRail "{0.title}"'.format(tr_case,
                                                               xu_case))
            raise Exception("Can't map some testrail cases")
        return dict(mapping)


def truncate_head(banner, text, max_len):
    max_text_len = min(max_len - len(banner), len(text))
    start = '...\n'
    if max_text_len < len(text):
        max_text_len -= len(start)
        text = start + text[-max_text_len:]
    return banner + text
