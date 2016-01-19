# TestRail xUnit Reporter

```
usage: report [-h] [--iso_link ISO_LINK] [--operation_system OPERATION_SYSTEM]
              [--iso_id ISO_ID] [--testrail-url TESTRAIL_URL]
              [--testrail-user TESTRAIL_USER]
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
  --iso_link ISO_LINK   link to iso
  --operation_system OPERATION_SYSTEM
                        deployed OpenStack operation system
  --iso_id ISO_ID       id of build Fuel iso
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