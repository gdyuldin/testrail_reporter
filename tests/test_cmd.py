import argparse
import itertools
import sys

import pytest
import six
import testrail

from xunit2testrail import cmd


if six.PY2:
    import mock
else:
    from unittest import mock


def test_filename_exists(tmpdir):
    p = tmpdir.mkdir("sub").join("report.xml")
    p.write("content")
    path = str(p)
    assert path == cmd.filename(path)


def test_filename_not_exists(tmpdir):
    p = tmpdir.mkdir("sub").join("report.xml")
    p.write("content")
    path = str(p)
    with pytest.raises(argparse.ArgumentTypeError):
        cmd.filename(path + 'foo')


def test_filename_not_a_file(tmpdir):
    s = tmpdir.mkdir("sub")
    p = s.join("report.xml")
    p.write("content")
    path = str(s)
    with pytest.raises(argparse.ArgumentTypeError):
        cmd.filename(path)


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


def test_reporter_map_cases(mocker, testrail_client_mock):
    mock_map_cases = mocker.patch('xunit2testrail.reporter.Reporter.map_cases')
    testargs = ['report', 'tests/xunit_files/report.xml']
    mocker.patch.object(sys, 'argv', testargs)
    cmd.main()
    assert 1 == mock_map_cases.call_count


def test_reporter_dry_run_table(mocker, capsys, testrail_client_mock):
    """Check that dry run prints table header."""
    from xunit2testrail.vendor.xunitparser import TestCase as XunitCase
    case_id = 2
    case_title = 'testrail_case'
    classname = 'a.TestClass'
    methodname = 'test_method'
    testrail_case = testrail.case.Case({'id': case_id, 'title': case_title})
    xunit_case = XunitCase(classname=classname, methodname=methodname)
    mocker.patch(
        'xunit2testrail.reporter.Reporter.map_cases',
        return_value={testrail_case: xunit_case})
    testargs = ['report', '--dry-run', 'tests/xunit_files/report.xml']
    mocker.patch.object(sys, 'argv', testargs)
    cmd.main()
    out, err = capsys.readouterr()
    assert all(
        s in out
        for s in ('ID', 'Tilte', 'Xunit case', str(case_id), case_title,
                  classname, methodname))


def test_dry_run_not_create_entities_in_testrail(mocker, testrail_client_mock):
    """Check that dry run mode is not create anything on testrail."""
    mocker.patch('xunit2testrail.reporter.Reporter.map_cases')
    add_mock = mocker.patch('testrail.TestRail.add')
    testargs = ['report', '--dry-run', 'tests/xunit_files/report.xml']
    mocker.patch.object(sys, 'argv', testargs)
    cmd.main()
    assert not add_mock.called


def test_dry_run_on_suite_creating(mocker, testrail_client_mock):
    """Check that nothing to be created on dry run."""
    add_mock = mocker.patch('testrail.TestRail.add')
    mocker.patch(
        'testrail.TestRail.milestone',
        return_value=testrail.milestone.Milestone({
            'name': 'milestone'
        }))
    mocker.patch('testrail.TestRail.suite', side_effect=[None, mock.Mock()])
    mocker.patch(
        'testrail.TestRail.section',
        side_effect=itertools.cycle([None, mock.Mock()]))
    mocker.patch(
        'testrail.TestRail.case',
        side_effect=itertools.cycle([None, mock.MagicMock()]))
    testargs = [
        'create_test_suite', '--dry-run', 'tests/xunit_files/report.xml'
    ]
    mocker.patch.object(sys, 'argv', testargs)
    cmd.create_test_suite()
    assert not add_mock.called
