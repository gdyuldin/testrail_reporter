#!/usr/bin/env python

from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()

setup(
    name='xunit2testrail',
    version='0.6.1',
    description='Report test results from xUnit xml file to TestRail',
    long_description=long_description,
    license='MIT',
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
    tests_require=[
        'pytest-mock',
        'pytest-capturelog',
        'httpretty',
    ],
)
