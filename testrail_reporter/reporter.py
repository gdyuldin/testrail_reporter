from __future__ import absolute_import, print_function

from functools import wraps
import logging
import re

from .testrail import Client as TrClient
from .testrail.client import Run
from .vendor import xunitparser


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
    def __init__(self, xunit_report, iso_id, env_description,
                 test_results_link, case_mapper, *args, **kwargs):
        self._config = {}
        self._cache = {}
        self.iso_id = iso_id
        self.plan_description = '#{0.iso_id} tests'.format(self)
        self.xunit_report = xunit_report
        self.env_description = env_description
        self.test_results_link = test_results_link
        self.case_mapper = case_mapper
        super(Reporter, self).__init__(*args, **kwargs)

    def config_testrail(self, base_url, username, password, milestone, project,
                        tests_suite):
        self._config['testrail'] = dict(base_url=base_url,
                                        username=username,
                                        password=password, )
        self.milestone_name = milestone
        self.project_name = project
        self.tests_suite_name = tests_suite

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

    def get_plan_name(self):
        return '{0.milestone_name} iso #{0.iso_id}'.format(self)

    def get_or_create_plan(self):
        """Get exists or create new TestRail Plan"""
        plan_name = self.get_plan_name()
        plan = self.project.plans.find(name=plan_name)
        if plan is None:
            plan = self.project.plans.add(name=plan_name,
                                          description=self.plan_description,
                                          milestone_id=self.milestone.id)
            logger.debug('Created new plan "{}"'.format(plan_name))
        else:
            logger.debug('Founded plan "{}"'.format(plan_name))
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

    def add_result_to_case(self, testrail_case, xunit_case):
        if xunit_case.success:
            status_name = 'passed'
        elif xunit_case.failed:
            status_name = 'failed'
        elif xunit_case.skipped:
            logger.debug(
                'Case {0.classname}.{0.methodname} is skipped'.format(
                    xunit_case))
            return
        elif xunit_case.errored:
            status_name = 'blocked'
        else:
            logger.warning('Unknown xunit case {} status {}'.format(
                xunit_case.methodname, xunit_case.result))
            return
        status_ids = [k
                      for k, v in self.testrail_statuses.items()
                      if v == status_name]
        if len(status_ids) == 0:
            logger.warning("Can't find status {} for result {}".format(
                status_name, xunit_case.methodname))
            return
        status_id = status_ids[0]
        test_result = xunit_case.message or 'Passed'
        report_url = self.get_jenkins_report_url(xunit_case)
        comment = '{}\nEnv: **{}**\n[Details]({})'.format(
            test_result, self.env_description, report_url)
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
        suite_name = "{} ({})".format(self.suite.name, self.env_description)
        description = ('Run **{suite}** on iso #{self.iso_id}. \n'
                       '[Test results]({self.test_results_link})').format(
                           suite=suite_name,
                           self=self)
        run = Run(name=suite_name,
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
