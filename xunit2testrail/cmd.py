#!/usr/bin/env python

import argparse
import logging
import os
import sys
import traceback
import warnings

from xunit2testrail import CaseMapper
from xunit2testrail import Reporter

warnings.simplefilter('always', DeprecationWarning)

if sys.version_info[0] == 3:
    str_cls = str
else:
    str_cls = eval('unicode')


def filename(string):
    if not os.path.exists(string):
        msg = "%r is not exists" % string
        raise argparse.ArgumentTypeError(msg)
    if not os.path.isfile(string):
        msg = "%r is not a file" % string
        raise argparse.ArgumentTypeError(msg)
    return string


def parse_args(args):
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
    defaults = {k: os.environ.get(k, v) for k, v in defaults.items()}

    parser = argparse.ArgumentParser(description='xUnit to testrail reporter')
    parser.add_argument(
        'xunit_report',
        type=filename,
        default=defaults['XUNIT_REPORT'],
        help='xUnit report XML file')

    parser.add_argument(
        '--xunit-name-template',
        type=str_cls,
        default=defaults['XUNIT_NAME_TEMPLATE'],
        help='template for xUnit cases to make id string')
    parser.add_argument(
        '--testrail-name-template',
        type=str_cls,
        default=defaults['TESTRAIL_NAME_TEMPLATE'],
        help='template for TestRail cases to make id string')

    parser.add_argument(
        '--env-description',
        type=str_cls,
        default=defaults['ENV_DESCRIPTION'],
        help='env deploy type description (for TestRun name)')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--iso-id',
        type=str_cls,
        default=defaults['ISO_ID'],
        help='id of build Fuel iso (DEPRECATED)')
    group.add_argument(
        '--testrail-plan-name',
        type=str_cls,
        default=defaults['TESTRAIL_PLAN_NAME'],
        help='name of test plan to be displayed in testrail')

    parser.add_argument(
        '--test-results-link',
        type=str_cls,
        default=defaults['TEST_RESULTS_LINK'],
        help='link to test job results')
    parser.add_argument(
        '--testrail-url',
        type=str_cls,
        default=defaults['TESTRAIL_URL'],
        help='base url of testrail')
    parser.add_argument(
        '--testrail-user',
        type=str_cls,
        default=defaults['TESTRAIL_USER'],
        help='testrail user')
    parser.add_argument(
        '--testrail-password',
        type=str_cls,
        default=defaults['TESTRAIL_PASSWORD'],
        help='testrail password')
    parser.add_argument(
        '--testrail-project',
        type=str_cls,
        default=defaults['TESTRAIL_PROJECT'],
        help='testrail project name')
    parser.add_argument(
        '--testrail-milestone',
        type=str_cls,
        default=defaults['TESTRAIL_MILESTONE'],
        help='testrail project milestone')
    parser.add_argument(
        '--testrail-suite',
        type=str_cls,
        default=defaults['TESTRAIL_TEST_SUITE'],
        help='testrail project suite name')
    parser.add_argument(
        '--send-skipped',
        action='store_true',
        default=False,
        help='send skipped cases to testrail')
    parser.add_argument(
        '--paste-url',
        type=str_cls,
        default=defaults['PASTE_BASE_URL'],
        help='paste service to send test case logs and trace')

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        default=False,
        help='Verbose mode')

    return parser.parse_args(args)


def main(args=None):

    args = args or sys.argv[1:]

    args = parse_args(args)

    if not args.testrail_plan_name:
        args.testrail_plan_name = ('{0.testrail_milestone} iso '
                                   '#{0.iso_id}').format(args)

        msg = ("--iso-id parameter is DEPRECATED. "
               "It is recommended to use --testrail-plan-name parameter.")
        warnings.warn(msg, DeprecationWarning)

    logger_dict = dict(stream=sys.stderr)
    if args.verbose:
        logger_dict['level'] = logging.DEBUG

    logging.basicConfig(**logger_dict)

    case_mapper = CaseMapper(
        xunit_name_template=args.xunit_name_template,
        testrail_name_template=args.testrail_name_template)

    reporter = Reporter(
        xunit_report=args.xunit_report,
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
        send_skipped=args.send_skipped)
    reporter.execute()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
