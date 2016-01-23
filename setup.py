#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    use_scm_version={'write_to': 'testrail_reporter/_version.py'},
    name='testrail_reporter',
    # version='0.0.3',
    description='Report test results from xUnit xml file to TestRail',
    author='Georgy Dyuldin',
    author_email='gdyuldin@mirantis.com',
    packages=find_packages(),
    scripts=['bin/report'],
    url="https://github.com/gdyuldin/testrail_reporter",
    setup_requires=[
        'requests',
        'pytest-runner',
        'setuptools_scm',
    ],
    tests_require=[
        'pytest-mock',
        'httpretty',
    ],
)
