#!/usr/bin/env python

from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()

setup(
    name='xunit2testrail',
    version='0.7.2',
    description='Report test results from xUnit xml file to TestRail',
    long_description=long_description,
    license='MIT',
    author='Georgy Dyuldin',
    author_email='gdyuldin@mirantis.com',
    packages=find_packages(),
    package_data={'': ['templates/*']},
    entry_points={
              'console_scripts': [
                  'report = xunit2testrail.cmd:main'
              ]
          },
    url="https://github.com/gdyuldin/testrail_reporter",
    install_requires=[
        'setuptools>=17.1',
        'requests>=2.4.2',
        'pytest-runner',
        'Jinja2',
        'six'
    ],
    extras_require={'test': [
        'pytest-mock',
        'pytest-capturelog',
        'requests-mock',
    ]},
)
