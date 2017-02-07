import sys

from xunit2testrail import cmd

import pytest


def test_parse_args_return_not_bytes():
    parsed_args = cmd.parse_args(
        ['--iso-id', '1', 'tests/xunit_files/report.xml'])
    for attr in dir(parsed_args):
        if not attr.startswith('_') and attr != 'xunit_report':
            assert not isinstance(getattr(parsed_args, attr), bytes)


def test_help(capsys, mocker):
    testargs = ['prog', '--help']
    mocker.patch.object(sys, 'argv', testargs)
    with pytest.raises(SystemExit):
        cmd.main()
    out, err = capsys.readouterr()
    assert not err
    assert 'xUnit to testrail reporter' in out
