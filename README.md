# TestRail xUnit Reporter

[![Build Status](https://travis-ci.org/gdyuldin/testrail_reporter.svg?branch=master)](https://travis-ci.org/gdyuldin/testrail_reporter)

```
usage: report [-h] [--env-description ENV_DESCRIPTION] [--iso-id ISO_ID]
              [--test-results-link TEST_RESULTS_LINK]
              [--testrail-url TESTRAIL_URL] [--testrail-user TESTRAIL_USER]
              [--testrail-password TESTRAIL_PASSWORD]
              [--testrail-project TESTRAIL_PROJECT]
              [--testrail-milestone TESTRAIL_MILESTONE]
              [--testrail-suite TESTRAIL_SUITE] [--verbose]
              xunit_report

Report to testrail

positional arguments:
  xunit_report          xUnit report XML file

optional arguments:
  -h, --help            show this help message and exit
  --env-description ENV_DESCRIPTION
                        env deploy type description (for TestRun name)
  --iso-id ISO_ID       id of build Fuel iso
  --test-results-link TEST_RESULTS_LINK
                        link to test job results
  --testrail-url TESTRAIL_URL
                        base url of testrail
  --testrail-user TESTRAIL_USER
                        testrail user
  --testrail-password TESTRAIL_PASSWORD
                        testrail password
  --testrail-project TESTRAIL_PROJECT
                        testrail project name
  --testrail-milestone TESTRAIL_MILESTONE
                        testrail project milestone
  --testrail-suite TESTRAIL_SUITE
                        testrail project suite name
  --verbose, -v         Verbose mode
```
