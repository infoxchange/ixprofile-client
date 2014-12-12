"""
Package configuration
"""
# pylint:disable=no-name-in-module,import-error
from distutils.core import setup
from setuptools import find_packages

with open('requirements.txt') as requirements, \
        open('test_requirements.txt') as test_requirements:
    setup(
        name='IXProfileClient',
        version='0.2.0',
        author='Infoxchange dev team',
        author_email='devs@infoxchange.net.au',
        packages=find_packages(),
        license='MIT',
        description='IX Profile Server client',
        long_description=open('README').read(),
        install_requires=requirements.read().splitlines(),
        test_requires=test_requirements.read().splitlines(),
    )
