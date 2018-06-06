import sys

import pytest

from xunit2testrail import cmd


def test_parse_args_return_not_bytes():
    parsed_args = cmd.parse_args(
        ['--iso-id', '1', 'tests/xunit_files/report.xml'])
    for attr in dir(parsed_args):
        if not attr.startswith('_') and attr != 'xunit_report':
            assert not isinstance(getattr(parsed_args, attr), bytes)


def test_help(capsys, mocker):
    testargs = ['report', '--help']
    mocker.patch.object(sys, 'argv', testargs)
    with pytest.raises(SystemExit):
        cmd.main()
    out, err = capsys.readouterr()
    assert not err
    assert 'xUnit to testrail reporter' in out


def test_reporter_map_cases(mocker):
    mock_map_cases = mocker.patch('xunit2testrail.reporter.Reporter.map_cases')
    testargs = ['report', 'tests/xunit_files/report.xml',
                '--testrail-plan-name', 'testplan']
    mocker.patch.object(sys, 'argv', testargs)
    cmd.main()
    assert 1 == mock_map_cases.call_count


def test_reporter_dry_run_table_header(mocker, capsys):
    """Check that dry run prints table header."""
    mocker.patch('xunit2testrail.reporter.Reporter.map_cases')
    testargs = ['report', '--dry-run', 'tests/xunit_files/report.xml',
                '--testrail-plan-name', 'testplan']
    mocker.patch.object(sys, 'argv', testargs)
    cmd.main()
    out, err = capsys.readouterr()
    assert all(s in out for s in ('ID', 'Tilte', 'Xunit case'))


@pytest.mark.parametrize('method',
                         ['get_or_create_plan', 'get_or_create_test_run'])
def test_dry_run_not_create_entities_in_testrail(mocker, method):
    """Check that dry run mode is not create anything on testrail."""
    mocker.patch('xunit2testrail.reporter.Reporter.map_cases')
    method_mock = mocker.patch('xunit2testrail.reporter.Reporter.' + method)
    testargs = ['report', '--dry-run', 'tests/xunit_files/report.xml',
                '--testrail-plan-name', 'testplan']
    mocker.patch.object(sys, 'argv', testargs)
    cmd.main()
    assert not method_mock.called
