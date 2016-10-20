from __future__ import absolute_import, print_function

from functools import wraps
import logging
import re
from six.moves.urllib import parse

from jinja2 import Environment, PackageLoader
import requests

from .testrail import Client as TrClient
from .testrail.client import Run
from .testrail.exceptions import NotFound
from .vendor import xunitparser
from .utils import truncate_head

logger = logging.getLogger(__name__)


def memoize(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        key = f.__name__
        cached = self._cache.get(key)
        if cached is None:
            cached = self._cache[key] = f(self, *args, **kwargs)
        return cached

    return wrapper


class Reporter(object):
    def __init__(self, xunit_report, env_description, test_results_link,
                 case_mapper, paste_url, *args, **kwargs):
        self._config = {}
        self._cache = {}
        self.xunit_report = xunit_report
        self.env_description = env_description
        self.test_results_link = test_results_link
        self.case_mapper = case_mapper
        self.paste_url = paste_url
        self.env = Environment(loader=PackageLoader('xunit2testrail'))

        super(Reporter, self).__init__(*args, **kwargs)

    def config_testrail(self, base_url, username, password, milestone, project,
                        tests_suite, plan_name, send_skipped=False):
        self._config['testrail'] = dict(base_url=base_url,
                                        username=username,
                                        password=password, )
        self.milestone_name = milestone
        self.project_name = project
        self.tests_suite_name = tests_suite
        self.plan_name = plan_name
        self.plan_description = '{plan_name} tests'.format(
            plan_name=self.plan_name)
        self.send_skipped = send_skipped

    @property
    def testrail_client(self):
        return TrClient(**self._config['testrail'])

    @property
    @memoize
    def project(self):
        return self.testrail_client.projects.find(name=self.project_name)

    @property
    @memoize
    def milestone(self):
        return self.project.milestones.find(name=self.milestone_name)

    @property
    @memoize
    def os_config(self):
        return self.project.configs.find(name='Operation System')

    @property
    @memoize
    def suite(self):
        return self.project.suites.find(name=self.tests_suite_name)

    @property
    @memoize
    def cases(self):
        return self.suite.cases()

    @property
    @memoize
    def testrail_statuses(self):
        return self.testrail_client.statuses

    def get_or_create_plan(self):
        """Get exists or create new TestRail Plan"""
        try:
            plan = self.project.plans.find(name=self.plan_name)
        except NotFound:
            plan = self.project.plans.add(name=self.plan_name,
                                          description=self.plan_description,
                                          milestone_id=self.milestone.id)
            logger.debug('Created new plan "{}"'.format(self.plan_name))
        else:
            logger.debug('Founded plan "{}"'.format(self.plan_name))
        return plan

    def get_xunit_test_suite(self):
        with open(self.xunit_report) as f:
            ts, tr = xunitparser.parse(f)
            return ts, tr

    def get_jenkins_report_url(self, xunit_case):
        module, _, classname = xunit_case.classname.rpartition('.')
        if module == '':
            module = '(root)'
        methodname = re.sub(r'[^a-zA-Z0-9_]', '_', xunit_case.methodname)
        return '{job}testReport/{module}/{classname}/{methodname}/'.format(
            job=self.test_results_link,
            module=module,
            classname=classname,
            methodname=methodname)

    def save_to_paste(self, xunit_case):
        max_paste_size = 65535
        chars_available = max_paste_size

        code = ''

        headers = {'trace': '### trace [python]\n',
                   'stdout': '### stdout.log\n',
                   'stderr': '### stderr.log\n'}

        trace = getattr(xunit_case, 'trace', None)

        if trace:
            code = truncate_head(headers['trace'], trace, chars_available)
            chars_available -= len(code) + 1

        stderr = getattr(xunit_case, 'stderr', None)
        if stderr:
            stderr = truncate_head(headers['stderr'], stderr, chars_available)
            chars_available -= len(stderr) + 1

        stdout = getattr(xunit_case, 'stdout', None)
        if stdout:
            code += '\n' + truncate_head(headers['stdout'], stdout,
                                         chars_available)

        if stderr:
            code += '\n' + stderr

        r = requests.post(
            parse.urljoin(self.paste_url, '/json/?method=pastes.newPaste'),
            json={
                'language': 'multi',
                'code': code
            })
        paste_id = r.json().get('data')
        if paste_id:
            return parse.urljoin(self.paste_url, '/show/{}/'.format(paste_id))

    def gen_testrail_comment(self, xunit_case):
        template = self.env.get_template('testrail_comment.md')
        jenkins_url = self.get_jenkins_report_url(xunit_case)
        paste_url = None
        if not xunit_case.success:
            try:
                paste_url = self.save_to_paste(xunit_case)
            except Exception as e:
                logger.warning(e)

        return template.render(xunit_case=xunit_case,
                               env_description=self.env_description,
                               jenkins_url=jenkins_url,
                               paste_url=paste_url)

    def add_result_to_case(self, testrail_case, xunit_case):
        if xunit_case.success:
            status_name = 'passed'
        elif xunit_case.failed:
            status_name = 'failed'
        elif xunit_case.skipped:
            if self.send_skipped:
                status_name = 'skipped'
            else:
                logger.debug('Case {0.classname}.{0.methodname} '
                             'is skipped'.format(xunit_case))
                return
        elif xunit_case.errored:
            status_name = 'blocked'
        else:
            logger.warning('Unknown xunit case {} status {}'.format(
                xunit_case.methodname, xunit_case.result))
            return
        status_ids = [k for k, v in self.testrail_statuses.items()
                      if v == status_name]
        if len(status_ids) == 0:
            logger.warning("Can't find status {} for result {}".format(
                status_name, xunit_case.methodname))
            return
        status_id = status_ids[0]
        comment = self.gen_testrail_comment(xunit_case)
        elasped = int(xunit_case.time.total_seconds())
        if elasped > 0:
            elasped = "{}s".format(elasped)
        testrail_case.add_result(status_id=status_id,
                                 elapsed=elasped,
                                 comment=comment)
        return testrail_case

    def find_testrail_cases(self, xunit_suite):
        cases = self.suite.cases()
        mapping = self.case_mapper.map(xunit_suite, cases)
        filtered_cases = []
        for testrail_case, xunit_case in mapping.items():
            if self.add_result_to_case(testrail_case, xunit_case):
                filtered_cases.append(testrail_case)
        cases[:] = filtered_cases
        return cases

    def create_test_run(self, plan, cases):
        run_name = "{0.env_description} <{0.tests_suite_name}>".format(self)
        description = ('Run **{run_name}** on #{plan_name}. \n'
                       '[Test results]({self.test_results_link})').format(
                           run_name=run_name,
                           plan_name=self.plan_name,
                           self=self)
        run = Run(name=run_name,
                  description=description,
                  suite_id=self.suite.id,
                  milestone_id=self.milestone.id,
                  config_ids=[],
                  case_ids=[x.id for x in cases], )
        plan.add_run(run)
        return run

    def print_run_url(self, test_run):
        print('[TestRun URL] {}'.format(test_run.url))

    def execute(self):
        xunit_suite, _ = self.get_xunit_test_suite()
        cases = self.find_testrail_cases(xunit_suite)
        if len(cases) == 0:
            logger.warning('No cases matched, programm will terminated')
            return
        plan = self.get_or_create_plan()
        test_run = self.create_test_run(plan, cases)
        test_run.add_results_for_cases(cases)
        self.print_run_url(test_run)
