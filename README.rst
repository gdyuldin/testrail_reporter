TestRail xUnit Reporter
=======================

.. image:: https://travis-ci.org/gdyuldin/testrail_reporter.svg?branch=master
   :target: https://travis-ci.org/gdyuldin/testrail_reporter

.. image:: https://codecov.io/gh/gdyuldin/testrail_reporter/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/gdyuldin/testrail_reporter


This reporter helps to send xUnit XML report from automated tests to
TestRail.

Matching rules
--------------

For correct reporting, reporter makes **indentifications strings** for
all xUnit and TestRail cases. Identification strings are makes by
templates - one for xUnit and one for TestRail Case. Templates are just
`Format
Strings <https://docs.python.org/2/library/string.html#format-string-syntax>`__.
Next reporter searchs xUnit testcase indentification string in all
TestRail cases indentifications strings.

xUnit template variables
''''''''''''''''''''''''

-  classname (like ``tempest.api.network.test_routers.RoutersIpV6Test``)
-  methodname (from report, like
   ``test_update_router_admin_state[id-a8902683-c788-4246-95c7-ad9c6d63a4d9]``)
-  id (extracts from ``methodname``, e.g. for ``test_a[(12345)]`` it
   will be ``12345``)
-  uuid (extracts from ``methodname``, e.g. for
   ``test_quotas[network,id-2390f766-836d-40ef-9aeb-e810d78207fb,network]``
   it will be ``2390f766-836d-40ef-9aeb-e810d78207fb``)

Argument name: ``--xunit-name-template``

Default value: ``{id}``

xUnit template may looks like ``'{classname}.{methodname}'`` or just
``'{id}'``.

TestRail template variables
'''''''''''''''''''''''''''

-  custom\_report\_label (Report Label in UI)
-  custom\_test\_group (Test Group in UI)
-  title

Argument name: ``--testrail-name-template``

Default value: ``{custom_report_label}``

Also possible to use other variables (full list here - `TestRail Api
Documentation <http://docs.gurock.com/testrail-api2/reference-cases#get_case>`__)

TestRail template may looks like ``'{custom_report_label}'`` or
``'{custom_test_group}.{title}'``.

Collisions
~~~~~~~~~~

If one xUnit case matches to more than one TestRail case or one TestRail
case matches to more than one xUnit case - reporter stops work, print
out this cases and exits with error.

Usage
-----

::

    usage: report [-h] [--xunit-name-template XUNIT_NAME_TEMPLATE]
                  [--testrail-name-template TESTRAIL_NAME_TEMPLATE]
                  [--env-description ENV_DESCRIPTION]
                  (--iso-id ISO_ID | --testrail-plan-name TESTRAIL_PLAN_NAME)
                  [--test-results-link TEST_RESULTS_LINK]
                  [--testrail-url TESTRAIL_URL] [--testrail-user TESTRAIL_USER]
                  [--testrail-password TESTRAIL_PASSWORD]
                  [--testrail-project TESTRAIL_PROJECT]
                  [--testrail-milestone TESTRAIL_MILESTONE]
                  [--testrail-suite TESTRAIL_SUITE] [--send-skipped]
                  [--paste-url PASTE_URL] [--verbose]
                  xunit_report

    Report to testrail

    positional arguments:
      xunit_report          xUnit report XML file

    optional arguments:
      -h, --help            show this help message and exit
      --xunit-name-template XUNIT_NAME_TEMPLATE
                            template for xUnit cases to make id string
      --testrail-name-template TESTRAIL_NAME_TEMPLATE
                            template for TestRail cases to make id string
      --env-description ENV_DESCRIPTION
                            env deploy type description (for TestRun name)
      --iso-id ISO_ID       id of build Fuel iso (DEPRECATED)
      --testrail-plan-name TESTRAIL_PLAN_NAME
                            name of test plan to be displayed in testrail
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
      --send-skipped        send skipped cases to testrail
      --paste-url PASTE_URL
                            paste service to send test case logs and trace
      --verbose, -v         Verbose mode
