"""
Package configuration
"""
from distutils.core import setup
from setuptools import find_packages

setup(
    name='IXProfileClient',
    version='0.1.0',
    author='Infoxchange Australia dev team',
    author_email='devs@infoxchange.net.au',
    packages=find_packages(),
    license='MIT',
    description='IX Profile Server client',
    long_description=open('README').read(),
    install_requires=[
        "Django >= 1.4.0",
        "django-social-auth >= 0.7.20",
        "pep8 >= 1.4.5",
        "pylint >= 0.27.0",
        "pylint-mccabe >= 0.1.2",
        "requests >= 1.1.0",
        "IXDjango >= 0.1.1",
        "IXWSAuth >= 0.1.1",
    ],
)
