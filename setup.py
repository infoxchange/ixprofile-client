"""
Package configuration
"""
from distutils.core import setup
from setuptools import find_packages

setup(
    name='IXProfileClient',
    version='0.1.0',
    author='Infoxchanhe Australia dev team',
    author_email='devs@infoxchange.net.au',
    packages=find_packages(),
    license='MIT',
    description='IX Profile Server client',
    long_description=open('README').read(),
    install_requires=[
        "Django >= 1.5.0",
        "flake8 >= 2.0",
        "pylint >= 0.27.0",
        "django-social-auth >= 0.7.20",
    ],
)
