from __future__ import absolute_import, print_function

import logging
import re
from six.moves.urllib import parse
from jinja2 import Environment, PackageLoader
import requests

from . import utils

logger = logging.getLogger(__name__)


class Reporter(object):
    def __init__(self, env_description, test_results_link,
                 case_mapper, paste_url, *args, **kwargs):
        self._config = {}
        self.env_description = env_description
        self.test_results_link = test_results_link
        self.case_mapper = case_mapper
        self.paste_url = paste_url
        self.env = Environment(loader=PackageLoader('xunit2testrail'))

        super(Reporter, self).__init__(*args, **kwargs)

    def config_testrail(self,
                        base_url,
                        username,
                        password,
                        milestone,
                        project,
                        tests_suite,
                        plan_name,
                        send_skipped=False,
                        use_test_run_if_exists=False):
        self.milestone_name = milestone
        self.project_name = project
        self.tests_suite_name = tests_suite
        self.plan_name = plan_name
        self.plan_description = '{plan_name} tests'.format(
            plan_name=self.plan_name)
        self.send_skipped = send_skipped
        self.use_test_run_if_exists = use_test_run_if_exists

        self.testrail_client = utils.get_testrail_client(username, password,
                                                         base_url, project)

    @property
    def milestone(self):
        return utils.get_milestone(self.testrail_client, self.milestone_name)

    @property
    def suite(self):
        return utils.get_suite(self.testrail_client, self.tests_suite_name)

    @property
    def cases(self):
        return self.testrail_client.cases(self.suite)

    @property
    def testrail_statuses(self):
        return self.testrail_client.statuses()

    def get_or_create_plan(self):
        """Get exists or create new TestRail Plan"""
        plan = self.testrail_client.plan(self.plan_name)
        if plan is None:
            plan = self.testrail_client.plan()
            plan.name = self.plan_name
            plan.description = self.plan_description
            plan.milestone = self.milestone
            plan = self.testrail_client.add(plan)
            logger.debug('Created new plan "{}"'.format(plan.name))
        else:
            logger.debug('Founded plan "{}"'.format(plan.name))
        return plan

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

        headers = {
            'trace': '### trace [python]\n',
            'stdout': '### stdout.log\n',
            'stderr': '### stderr.log\n'
        }

        trace = getattr(xunit_case, 'trace', None)

        if trace:
            code = utils.truncate_head(headers['trace'], trace,
                                       chars_available)
            chars_available -= len(code) + 1

        stderr = getattr(xunit_case, 'stderr', None)
        if stderr:
            stderr = utils.truncate_head(headers['stderr'], stderr,
                                         chars_available)
            chars_available -= len(stderr) + 1

        stdout = getattr(xunit_case, 'stdout', None)
        if stdout:
            code += '\n' + utils.truncate_head(headers['stdout'], stdout,
                                               chars_available)

        if stderr:
            code += '\n' + stderr

        r = requests.post(
            parse.urljoin(self.paste_url, '/json/?method=pastes.newPaste'),
            json={'language': 'multi',
                  'code': code})
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

        return template.render(
            xunit_case=xunit_case,
            env_description=self.env_description,
            jenkins_url=jenkins_url,
            paste_url=paste_url)

    def get_cases_results_data(self, xunit_case):
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
        statuses = [s for s in self.testrail_statuses if s.name == status_name]
        if len(statuses) == 0:
            logger.warning("Can't find status {} for result {}".format(
                status_name, xunit_case.methodname))
            return
        status = statuses[0]

        comment = self.gen_testrail_comment(xunit_case)
        elasped = int(xunit_case.time.total_seconds())
        if elasped > 0:
            elasped = "{}s".format(elasped)

        return {'status': status, 'elasped': elasped, 'comment': comment}

    def map_cases(self, xunit_suite):
        return self.case_mapper.map(xunit_suite, self.cases)

    def fill_case_results(self, mapping):
        filtered_cases = {}
        for testrail_case, xunit_case in mapping.items():
            result_data = self.get_cases_results_data(xunit_case)
            if result_data:
                filtered_cases[testrail_case] = result_data
        return filtered_cases

    def create_test_run(self, run_name, plan, cases_with_results):
        description = ('Run **{name}** on #{plan_name}. \n'
                       '[Test results]({self.test_results_link})').format(
                           name=run_name,
                           plan_name=self.plan_name,
                           self=self)
        run = self.testrail_client.run()
        run.name = run_name
        run.description = description
        run.suite = self.suite
        run.milestone = self.milestone
        run.cases = cases_with_results.keys()
        run.plan = plan
        run = self.testrail_client.add(run)
        return run

    def get_or_create_test_run(self, plan, cases_with_results):
        # run name can't have whitespaces in the beginning or in the end
        # because they are silently trimmed by server side (API or database)
        run_name = ("{0.env_description} "
                    "<{0.tests_suite_name}>").format(self).strip()
        if self.use_test_run_if_exists:
            try:
                entry = next(entry for entry in plan.entries
                             if entry.name == run_name and entry.runs)
                logger.debug('Found test run "{}"'.format(run_name))
                return entry.runs[-1]
            except StopIteration:
                logger.debug('Test run "{}" not found'.format(run_name))
        return self.create_test_run(run_name, plan, cases_with_results)

    def fill_run_with_results(self, test_run, cases_with_results):
        for test in self.testrail_client.tests(test_run):
            case_id = test.raw_data()['case_id']
            result_data = next(r for c, r in cases_with_results.items()
                               if c.id == case_id)
            result = self.testrail_client.result()
            result.status = result_data['status']
            result.elasped = result_data['elasped']
            result.comment = result_data['comment']
            result.test = test
            self.testrail_client.add(result)

    def print_run_url(self, test_run):
        print('[TestRun URL] {}'.format(test_run.url))
