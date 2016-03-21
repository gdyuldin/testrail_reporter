Changelog
=========

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


