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
    package_data={'': ['templates/*']},
    scripts=['bin/report'],
    url="https://github.com/gdyuldin/testrail_reporter",
    install_requires=[
        'setuptools>=17.1',
        'requests>=2.4.2',
        'pytest-runner',
        'Jinja2',
        'six'
    ],
    setup_requires=['setuptools_scm'],
    tests_require=[
        'pytest-mock',
        'pytest-capturelog',
        'httpretty',
    ],
)
