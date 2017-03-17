Changelog
=========

v0.7.1 (2017-03-17)
-------------------

Fix
~~~

- Extracting vaues from xunit cases, that contains 'None' [Georgy
  Dyuldin]

Other
~~~~~

- Merge pull request #4 from artem-panchenko/updateTestRunFeature.
  [Georgy Dyuldin]

  Add possibility to update existing test run

- Add possibility to update existing test run. [Artem Panchenko]

  Introduce new option '--testrail-run-update' which
  allows to complement existing test run by adding
  missing tests to the plan entry. It allows to split
  a suite in few threads, then run tests and report
  results into single test run fully independently.

v0.7.0 (2017-02-07)
-------------------

New
~~~

- Add python3 support. [Georgy Dyuldin]

Other
~~~~~

- Fix command args parsing. [Georgy Dyuldin]

v0.6.1 (2016-10-20)
-------------------

Fix
~~~

- Change package name in MANIFEST.in. [Georgy Dyuldin]

v0.6.0 (2016-10-20)
-------------------

New
~~~

- Switch to `bumpversion` [Georgy Dyuldin]

Other
~~~~~

- Rename package to xunit2testrail. [Georgy Dyuldin]

- Update CHANGELOG.rst. [Georgy Dyuldin]

0.5.3 (2016-10-19)
------------------

Fix
~~~

- Add setuptools version to fix pbr issue. [Georgy Dyuldin]

  http://docs.openstack.org/developer/pbr/compatibility.html#evaluate-marker

- Add six to requirements. [Georgy Dyuldin]

Other
~~~~~

- Update CHANGELOG.rst. [Georgy Dyuldin]

- Add PyPI deploy on travis. [Georgy Dyuldin]

- Add codecov.io. [Georgy Dyuldin]

0.5.2 (2016-09-20)
------------------

New
~~~

- Add '--paste-url' parameter to reporter arguments. [Georgy Dyuldin]

  This parameter allow to override default paste (lodgeit) service to
  store logs and traces to.

0.5.1 (2016-08-02)
------------------

New
~~~

- Add `--send-skipped` flag to reporter. [Georgy Dyuldin]

Fix
~~~

- Add templates to sdist and install. [Georgy Dyuldin]

0.5.0 (2016-05-24)
------------------

New
~~~

- Add storing test info to paste.openstack.org. [Georgy Dyuldin]

  Now test traceback, stdout log, stderr log storing on
  paste.openstack.org in case test failed or errored.

- TestRail report comment format with template. [Georgy Dyuldin]

  This template show trace direct on TestRail comment message.

Fix
~~~

- Reporter plan creating. [Georgy Dyuldin]

Other
~~~~~

- Merge pull request #3 from gdyuldin/paste. [Georgy Dyuldin]

- Merge pull request #2 from gdyuldin/paste. [Georgy Dyuldin]

  New template for testrail comment and storing results on paste.openstack.org

0.4.4 (2016-05-18)
------------------

Fix
~~~

- Issue with '-id' strip on case. [Georgy Dyuldin]

  In case matching group ends with any of symbol '-', 'i', 'd', this
  symbols was removed from group. Now this behavior is fixed.

0.4.3 (2016-04-20)
------------------

Fix
~~~

- UnicodeEncodeError on non-ascii xunit case message. [Georgy Dyuldin]

- Bug with UnicodeDecodeError on mapping. [Georgy Dyuldin]

  This bug was appear if testrail cases contains non-ascii symbols in
  matching fields.

Other
~~~~~

- Merge pull request #1 from AlexGromov/test_plan_name_param. [Georgy
  Dyuldin]

  Test plan name param

- Applying comments. [Alexander Gromov]

- Applying comments. [Alexander Gromov]

- Added --test-plan-name parameter. [Alexander Gromov]

  Added --test-plan-name parameter so that we can manually set test plan
  name without using --iso-id parameter. This way is considered to be more
  common as we can use it to send reports for previous versions of MOS such
  as MOS 8.0.

  --iso-id parameter is considered to be DEPRECATED now.

0.4.2 (2016-04-08)
------------------

Fix
~~~

- Skip cases, which not suitable to template. [Georgy Dyuldin]

  This patch adds checks for xUnit case **identification string** not
  contains None. In case it contains - such results will be ignored, with
  warning to log.

- TestRail Cases creation. [Georgy Dyuldin]

0.4.1 (2016-03-21)
------------------

Fix
~~~

- Removed hardcoded test plan name. [Georgy Dyuldin]

0.4.0 (2016-03-21)
------------------

New
~~~

- Matching cases on template-based rules. [Georgy Dyuldin]

  Now cases match by `identification strings`, which are generated with
  templates from cases.

- Matching logic was changed. [Georgy Dyuldin]

  This patch changes Testrail TestCases and xUnit test methods results
  matching method. Now each result name (contained className and
  methodName) compare with special field in Testrail
  ('custom_report_label' by default), and if Testrail field value
  contains in full test name - this result and TestCase marked as pair.
  If there are any collision after compare - reporter will raise
  an Exception.

  Matching field in TestRail Case are configurable through evironment
  variable 'TESTRAIL_MATCHING_FIELD' or call parameter
  '--testrail-matching-field'.

0.3.3 (2016-02-10)
------------------

Fix
~~~

- Add retrying on 429 HTTP response from testrail. [Georgy Dyuldin]

0.3.2 (2016-02-09)
------------------

Fix
~~~

- Remove unnecessary call parameters. [Georgy Dyuldin]

0.3.1 (2016-02-05)
------------------

Fix
~~~

- Jenkins test result URL builder. [Georgy Dyuldin]

0.3.0 (2016-02-02)
------------------

New
~~~

- Test result has link to jenkins. [Georgy Dyuldin]

0.2.2 (2016-01-27)
------------------

Fix
~~~

- Remove skipped tests from report. [Georgy Dyuldin]

- Corrected matching of tempest uuid. [Georgy Dyuldin]

0.2.1 (2016-01-25)
------------------

Fix
~~~

- Add default logging handler. [Georgy Dyuldin]

- Setuptools older than 12  _version.py issue. [Georgy Dyuldin]

- Setup.py requirements. [Georgy Dyuldin]

0.2 (2016-01-23)
----------------

- Add TestRun description, minor fixes. [Georgy Dyuldin]

0.0.3 (2016-01-23)
------------------

- Add TestRun description, minor fixes. [Georgy Dyuldin]

- TestRun creates with only matched cases. [Georgy Dyuldin]

- Fix setup.py. [Georgy Dyuldin]

- Add matching tempest uuid, work with error cases. [Georgy Dyuldin]

  If test name in report contains `[id-<uuid>]`, this uuid will use to
  match testrail case
  If test errored, testrail case marked as Blocked

- Remove configuration, add env_description. [Georgy Dyuldin]

- Add checks for http answer, add get method to Item. [Georgy Dyuldin]

- Some improvements. [Georgy Dyuldin]


