"""
Unit tests against the real profile server
"""

from __future__ import absolute_import

import os
import unittest

from django.conf import settings

from ...docker_settings import (
    PROFILE_SERVER,
    PROFILE_SERVER_KEY,
    PROFILE_SERVER_SECRET,
)
from ...webservice import UserWebService

settings_monkeypatches = {}  # pylint:disable=invalid-name
SSL_CA_FILE = os.environ.get('SSL_CA_FILE')


def set_django_setting(name, value):
    """
    Set a Django setting
    """
    if name not in settings_monkeypatches:
        settings_monkeypatches[name] = getattr(settings, name)

    # pylint:disable=protected-access
    setattr(settings._wrapped, name, value)


def reset_django_settings():
    """
    Restore Django settings
    """
    for name, value in settings_monkeypatches.items():
        # pylint:disable=protected-access
        setattr(settings._wrapped, name, value)


class RealProfileServerTestCase(unittest.TestCase):
    """
    Base Test Case for testing against the real profile server.
    These tests only run when the following ENV variables are set:
    PROFILE_SERVER_URL=https://KEY:SECRET@profile.server
    SSL_CA_FILE=path/to/ssl_ca_certificate.crt
    """

    profile_server = None

    @classmethod
    def setUpClass(cls):
        """
        Initialise test case
        """
        if not PROFILE_SERVER:
            raise unittest.case.SkipTest("Profile Server not configured")
        if not SSL_CA_FILE:
            raise unittest.case.SkipTest("SSL_CA_FILE not configured")

        set_django_setting('PROFILE_SERVER', PROFILE_SERVER)
        set_django_setting('PROFILE_SERVER_KEY', PROFILE_SERVER_KEY)
        set_django_setting('PROFILE_SERVER_SECRET', PROFILE_SERVER_SECRET)
        set_django_setting('SSL_CA_FILE', SSL_CA_FILE)

        cls.profile_server = UserWebService()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up after test case
        """
        reset_django_settings()
