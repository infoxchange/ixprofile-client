"""
Package configuration
"""
# pylint:disable=no-name-in-module,import-error
from setuptools import find_packages

from distutils.core import setup

with open('requirements.txt') as requirements, \
        open('test_requirements.txt') as test_requirements:
    setup(
        name='IXProfileClient',
        version='1.1.0',
        author='Infoxchange dev team',
        author_email='devs@infoxchange.org',
        url='http://pypi.python.org/pypi/ixprofile-client/',
        packages=find_packages(),
        license='MIT',
        description='IX Profile Server client',
        long_description=open('README.md').read(),
        install_requires=requirements.read().splitlines(),
        test_requires=test_requirements.read().splitlines(),
    )
