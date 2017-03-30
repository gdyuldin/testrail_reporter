import pytest

from xunit2testrail.testrail import client
from xunit2testrail import utils

xfail = pytest.mark.xfail


@pytest.fixture
def template_mapper():
    return utils.TemplateCaseMapper(
        xunit_name_template=u'{id}',
        testrail_name_template=u'{custom_report_label}')


@pytest.mark.parametrize(
    'case_name, expected_id',
    (('test_ban_l3_agent[once][(12345)]', '12345'),
     ('test_ban_l3_agent_54321[once][(12345)]', '12345'),
     ('12345_test_ban_l3_agent[once]', None),
     ('test_ban_l3_agent_123', None),
     ('test_ban_l3_agent_12345', None),
     ('test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb]', None), ))
def test_extract_case_id(case_name, expected_id):
    assert utils.find_id(case_name) == expected_id


@pytest.mark.parametrize(
    'case_name, expected_id',
    (('test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb]',
      '2390f766-836d-40ef-9aeb-e810d78207fb'),
     ('test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fb,network]',
      '2390f766-836d-40ef-9aeb-e810d78207fb'),
     ('test_quotas[network,id-2390f766-836d-40ef-9aeb-e810d78207fb,network]',
      '2390f766-836d-40ef-9aeb-e810d78207fb'),
     ('test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207fg]', None),
     ('test_quotas[id-2390f766-836d-40ef-9aeb-e810d78207f]', None), ))
def test_extract_case_uuid(case_name, expected_id):
    assert utils.find_uuid(case_name) == expected_id


@pytest.mark.parametrize('x_tpl, tr_tpl, xcase_data, tcase_data, map_len', (
    (
        '{id}',
        '{custom_report_label}',
        {'classname': 'a', 'methodname': 'b[(12345)]'},
        {'custom_report_label': '12345'},
        1
    ),
    (
        '{id}',
        '{custom_test_group}',
        {'classname': 'a', 'methodname': 'b[(12345)]'},
        {'custom_report_label': '12345', 'custom_test_group': '1234'},
        0
    ),
    (
        '{classname}.{methodname}',
        '{title}',
        {'classname': 'a', 'methodname': 'b'},
        {'title': 'a.b'},
        1
    ),
    (
        '{classname}.{methodname}',
        '{title}',
        {'classname': 'a', 'methodname': 'b[None]'},
        {'title': 'a.b[None]'},
        1
    ),
))  # yapf: disable
def test_match_templates(x_tpl, tr_tpl, template_mapper, map_len, xcase_data,
                         tcase_data):
    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase
    xunit_case = XunitCase(**xcase_data)
    case = client.Case(**tcase_data)

    template_mapper.xunit_name_template = x_tpl
    template_mapper.testrail_name_template = tr_tpl
    result = template_mapper.get_suitable_cases(xunit_case, [case])
    assert len(result) == map_len


@pytest.mark.parametrize(
    'methodname, match_value, x_name_template, map_len',
    (('test_add', 'test_add', '{methodname}', 1),
     (u'test_a', u'test_b\u2019', u'{methodname}', 0),
     ('test_a', 'test_ab', '{methodname}', 0),
     ('test_ab', 'test_a', '{methodname}', 0),
     ('test_a[(12345)]', '12345', '{id}', 1),
     ('test_a[(112345)]', '1234', '{id}', 0),
     ('test_a[(12345)]', '112345', '{id}', 0),
     ('test_a[(12345)]', '123456', '{id}', 0),
     ('test_a[(123456)]', '12345', '{id}', 0),
     ('test_a[12345]', '12345', '{id}', 0),
     ('test_a[(12345)][id-2390f766-836d-40ef-9aeb-e810d78207fb]',
      '2390f766-836d-40ef-9aeb-e810d78207fb', '{uuid}', 1),
     ('test_a[(12345)][id-2390f766-836d-40ef-9aeb-e810d78207fb]', '12345',
      '{id}', 1), ))
def test_match_case(template_mapper, methodname, match_value, x_name_template,
                    map_len):
    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase
    xunit_case = XunitCase(classname='a.b.C', methodname=methodname)
    case = client.Case(custom_report_label=match_value)
    template_mapper.xunit_name_template = x_name_template
    result = template_mapper.get_suitable_cases(xunit_case, [case])
    assert len(result) == map_len


def test_empty_xunit_id(template_mapper, caplog):
    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase
    xunit_case = XunitCase(classname='a.b.C', methodname='test_e[1]')
    template_mapper.xunit_name_template = '{id}'
    case = client.Case(custom_report_label=None)
    result = template_mapper.get_suitable_cases(xunit_case, [case])
    assert case not in result
    assert str(xunit_case) in caplog.text


def check_mapping(result, expected_dict):
    __tracebackhide__ = True
    result_dict = {k.custom_report_label: v.methodname
                   for k, v in result.items()}
    assert expected_dict == result_dict


@pytest.mark.parametrize('xunit_names, testrail_names, expected', (
    (
        [],
        [],
        {}
    ),
    (
        ['test_a[(12345)]'],
        ['12345'],
        {'12345': 'test_a[(12345)]'}
    ),
    (
        ['test_a[(12345)]'],
        ['12345', 'test_b'],
        {'12345': 'test_a[(12345)]'}
    ),
    xfail((
        ['test_a[(12345)]', 'test_b[(12345)]'],
        ['12345'],
        {}
    )),
    xfail((
        ['test_a[(12345)]'],
        ['12345', '12345'],
        {}
    )),
))  # yapf: disable
def test_map_cases(template_mapper, xunit_names, testrail_names, expected):
    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase
    xunit_cases = [XunitCase(classname='a.b.C',
                             methodname=x) for x in xunit_names]
    testrail_cases = [client.Case(custom_report_label=x,
                           title=x) for x in testrail_names]
    check_mapping(template_mapper.map(xunit_cases, testrail_cases), expected)


@pytest.mark.parametrize('xunit_names, testrail_names, log_strings', (
    (
        [],
        [],
        []
    ),
    (
        ['test_a[(12345)]', 'test_b[(12345)]'],
        ['12345'],
        ['test_a[(12345)]', 'test_b[(12345)]', 'title_12345']
    ),
    (
        ['test_a[(12345)]'],
        ['12345', '12345'],
        ['test_a[(12345)]', 'title_12345']
    ),
))  # yapf: disable
def test_error_map_logging(template_mapper, xunit_names, testrail_names,
                           log_strings, caplog):
    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase
    xunit_cases = [
        XunitCase(classname='a.b.C', methodname=x) for x in xunit_names
    ]
    testrail_cases = [
        client.Case(custom_report_label=x, title='title_{}'.format(x))
        for x in testrail_names
    ]
    try:
        template_mapper.map(xunit_cases, testrail_cases)
    except Exception:
        pass
    assert all([x in caplog.text for x in log_strings])


def test_no_testrail_case_logging(caplog, template_mapper):
    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase

    xunit_case = XunitCase(classname='a.b.C', methodname='d[(12345)]')
    testrail_case = client.Case(custom_report_label='123456')
    template_mapper.map([xunit_case], [testrail_case])
    expected = "`{}` doesn't match".format(xunit_case)
    assert expected in caplog.text


@pytest.mark.parametrize('banner, text, max_length, expected',
                         (
                          ('foo\n', 'bar and bar', 15, 'foo\nbar and bar'),
                          ('foo\n', 'bar and bar', 14, 'foo\n...\nnd bar'),
                          ))
def test_truncate_head(banner, text, max_length, expected):
    assert utils.truncate_head(banner, text, max_length) == expected
