#!/usr/bin/env python

from setuptools import setup

setup(
    name='testrail_reporter',
    version='0.0.1',
    description='Report test results from xUnit xml file to TestRail',
    author='Georgy Dyuldin',
    author_email='gdyuldin@mirantis.com',
    packages=['reporter'],
    scripts=['bin/report'],
    url="https://github.com/gdyuldin/testrail_reporter",
    setup_requires=[
        'requests',
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'httpretty'
    ],
)
