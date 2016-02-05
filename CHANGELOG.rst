Changelog
=========

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


