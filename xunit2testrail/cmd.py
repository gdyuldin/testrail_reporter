#!/usr/bin/env python

import argparse
import functools
import itertools
import logging
import os
import sys
import textwrap
import traceback
import warnings

import prettytable

from xunit2testrail import TemplateCaseMapper
from xunit2testrail import Reporter
from xunit2testrail import utils

warnings.simplefilter('always', DeprecationWarning)
logger = logging.getLogger(__name__)

if sys.version_info[0] == 3:
    str_cls = str
else:
    str_cls = eval('unicode')


logger_cfg = dict(stream=sys.stderr, format='%(levelname)-8s %(message)s',
                  level=logging.INFO)


def filename(string):
    """Filename argument parser."""
    if not os.path.exists(string):
        msg = "%r is not exists" % string
        raise argparse.ArgumentTypeError(msg)
    if not os.path.isfile(string):
        msg = "%r is not a file" % string
        raise argparse.ArgumentTypeError(msg)
    return string


def get_default(key):
    """Default parses values."""
    defaults = {
        'TESTRAIL_URL': 'https://mirantis.testrail.com',
        'TESTRAIL_USER': 'user@example.com',
        'TESTRAIL_PASSWORD': 'password',
        'TESTRAIL_PROJECT': 'Mirantis OpenStack',
        'TESTRAIL_MILESTONE': '9.0',
        'TESTRAIL_TEST_SUITE': '[{0.testrail_milestone}] MOSQA',
        'XUNIT_REPORT': 'report.xml',
        'XUNIT_NAME_TEMPLATE': '{id}',
        'TESTRAIL_NAME_TEMPLATE': '{custom_report_label}',
        'ISO_ID': None,
        'TESTRAIL_PLAN_NAME': None,
        'ENV_DESCRIPTION': '',
        'TEST_RESULTS_LINK': '',
        'PASTE_BASE_URL': 'http://srv99-bud.infra.mirantis.net:5000/'
    }

    return os.environ.get(key, defaults[key])


def common_parser():
    """Common testrail arguments parser."""

    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument(
        '--testrail-url',
        type=str_cls,
        default=get_default('TESTRAIL_URL'),
        help='base url of testrail')
    parent_parser.add_argument(
        '--testrail-user',
        type=str_cls,
        default=get_default('TESTRAIL_USER'),
        help='testrail user')
    parent_parser.add_argument(
        '--testrail-password',
        type=str_cls,
        default=get_default('TESTRAIL_PASSWORD'),
        help='testrail password')
    parent_parser.add_argument(
        '--testrail-project',
        type=str_cls,
        default=get_default('TESTRAIL_PROJECT'),
        help='testrail project name')
    parent_parser.add_argument(
        '--testrail-milestone',
        type=str_cls,
        default=get_default('TESTRAIL_MILESTONE'),
        help='testrail project milestone')
    parent_parser.add_argument(
        '--testrail-suite',
        type=str_cls,
        default=get_default('TESTRAIL_TEST_SUITE'),
        help='testrail project suite name')
    parent_parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        default=False,
        help='Do not modify testrail information')
    parent_parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        default=False,
        help='Verbose mode')

    parent_parser.add_argument(
        'xunit_report', type=filename, help='xUnit report XML file')

    return parent_parser


def parse_args(args):
    """Parse args to reporter."""
    parser = argparse.ArgumentParser(
        description='xUnit to testrail reporter',
        parents=[common_parser()],
        prog="report")

    parser.add_argument(
        '--xunit-name-template',
        type=str_cls,
        default=get_default('XUNIT_NAME_TEMPLATE'),
        help='template for xUnit cases to make id string')
    parser.add_argument(
        '--testrail-name-template',
        type=str_cls,
        default=get_default('TESTRAIL_NAME_TEMPLATE'),
        help='template for TestRail cases to make id string')

    parser.add_argument(
        '--env-description',
        type=str_cls,
        default=get_default('ENV_DESCRIPTION'),
        help='env deploy type description (for TestRun name)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--iso-id',
        type=str_cls,
        default=get_default('ISO_ID'),
        help='id of build Fuel iso (DEPRECATED)')
    group.add_argument(
        '--testrail-plan-name',
        type=str_cls,
        default=get_default('TESTRAIL_PLAN_NAME'),
        help='name of test plan to be displayed in testrail')

    parser.add_argument(
        '--test-results-link',
        type=str_cls,
        default=get_default('TEST_RESULTS_LINK'),
        help='link to test job results')
    parser.add_argument(
        '--send-skipped',
        action='store_true',
        default=False,
        help='send skipped cases to testrail')
    parser.add_argument(
        '--paste-url',
        type=str_cls,
        default=get_default('PASTE_BASE_URL'),
        help='paste service to send test case logs and trace')
    parser.add_argument(
        '--testrail-run-update',
        dest='use_test_run_if_exists',
        action='store_true',
        default=False,
        help='don\'t create new test run if such already exists')

    return parser.parse_args(args)


def create_test_suite(args=None):
    """Create testrail suite for xUnit report."""
    args = args or sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Create testrail suite from xUnit report',
        parents=[common_parser()],
        prog="create_test_suite")

    args = parser.parse_args(args)

    if args.verbose:
        logger_cfg['level'] = logging.DEBUG

    logging.basicConfig(**logger_cfg)

    client = utils.get_testrail_client(
        args.testrail_user, args.testrail_password, args.testrail_url,
        args.testrail_project)
    project = client.project(args.testrail_project)

    milestone = utils.get_milestone(client, args.testrail_milestone)

    suite = client.suite(args.testrail_suite)
    if suite is None:
        suite = client.suite()
        suite.name = args.testrail_suite
        suite.description = 'Autogenerated from xUnit'
        suite.project = project
        if not args.dry_run:
            suite = client.add(suite)
            logging.info('Suite created: {}'.format(suite.url))
        else:
            logging.info('Suite to be created: {}'.format(suite.name))
    else:
        logging.info('Suite found: {}'.format(suite.url))

    xunit_cases = utils.get_xunit_cases(args.xunit_report)
    key_fn = lambda x: x.classname  # noqa: E731
    xunit_cases = sorted(xunit_cases, key=key_fn)
    for path, group in itertools.groupby(xunit_cases, key_fn):
        section = client.section(path, suite)
        if section is None:
            section = client.section()
            section.suite = suite
            section.name = path
            if args.dry_run:
                logger.info('Section to be created: {}'.format(section.name))
            else:
                section = client.add(section)
        for xunit_case in group:
            case = client.case(xunit_case.methodname, suite)
            if case is None:
                case = client.case()
                case.milestone = milestone
                case.section = section
                case.title = xunit_case.methodname
                case._content['custom_report_label'] = xunit_case.classname
                case._content['custom_qa_team'] = 1
                case._content['custom_test_case_steps'] = []
                if args.dry_run:
                    logger.info('Case to be created: {}'.format(case.title))
                else:
                    client.add(case)


def print_mapping_table(mapping, wrap=60):
    """Print mapping result table."""
    pt = prettytable.PrettyTable(field_names=['ID', 'Tilte', 'Xunit case'])
    pt.align = 'l'
    wrapper = functools.partial(
        textwrap.fill, width=wrap, break_long_words=False)
    for testrail_case, xunit_case in mapping.items():
        xunit_str = '{0.methodname}\n({0.classname})'.format(xunit_case)
        pt.add_row([
            testrail_case.id, wrapper(testrail_case.title), wrapper(xunit_str)
        ])
    print(pt)


def main(args=None):

    args = args or sys.argv[1:]

    args = parse_args(args)

    if not args.testrail_plan_name:
        args.testrail_plan_name = ('{0.testrail_milestone} iso '
                                   '#{0.iso_id}').format(args)

        msg = ("--iso-id parameter is DEPRECATED. "
               "It is recommended to use --testrail-plan-name parameter.")
        warnings.warn(msg, DeprecationWarning)

    if args.verbose:
        logger_cfg['level'] = logging.DEBUG

    logging.basicConfig(**logger_cfg)

    case_mapper = TemplateCaseMapper(
        xunit_name_template=args.xunit_name_template,
        testrail_name_template=args.testrail_name_template)

    reporter = Reporter(
        env_description=args.env_description,
        test_results_link=args.test_results_link,
        case_mapper=case_mapper,
        paste_url=args.paste_url)
    suite = args.testrail_suite.format(args)
    reporter.config_testrail(
        base_url=args.testrail_url,
        username=args.testrail_user,
        password=args.testrail_password,
        milestone=args.testrail_milestone,
        project=args.testrail_project,
        plan_name=args.testrail_plan_name,
        tests_suite=suite,
        send_skipped=args.send_skipped,
        use_test_run_if_exists=args.use_test_run_if_exists)

    xunit_suite = list(utils.get_xunit_cases(args.xunit_report))
    mapping = reporter.map_cases(xunit_suite)
    if not args.dry_run:
        cases_with_results = reporter.fill_case_results(mapping)
        if len(cases_with_results) == 0:
            logger.warning('No cases matched, programm will terminated')
            return
        plan = reporter.get_or_create_plan()
        test_run = reporter.get_or_create_test_run(plan, cases_with_results)
        reporter.fill_run_with_results(test_run, cases_with_results)
        reporter.print_run_url(test_run)
    else:
        print_mapping_table(mapping)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
