from xunit2testrail import cmd


def test_parse_args_return_not_bytes():
    parsed_args = cmd.parse_args(['--iso-id', '1',
                                 'tests/xunit_files/report.xml'])
    for attr in dir(parsed_args):
        if not attr.startswith('_') and attr != 'xunit_report':
            assert not isinstance(getattr(parsed_args, attr), bytes)
