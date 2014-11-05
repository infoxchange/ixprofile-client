"""
Test Lettuce Steps
"""

from __future__ import absolute_import

import os
import unittest

from django.conf import settings
from mock import MagicMock
# pylint:disable=no-name-in-module
from nose.tools import assert_equals, assert_in

from ..docker_settings import (
    PROFILE_SERVER,
    PROFILE_SERVER_KEY,
    PROFILE_SERVER_SECRET,
)
from ..webservice import UserWebService

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


class TestRealProfileServer(unittest.TestCase):
    """
    Test real profile server, these tests only run when the ENV variables are
    set:
    PROFILE_SERVER_URL=https://KEY:SECRET@profile.server
    SSL_CA_FILE=path/to/ssl_ca_certificate.crt
    """

    APP = 'ixprofile_client_test'
    test_email = 'bashful@infoxchange.net.au'
    user = MagicMock(email=test_email)

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

        # Remove any preference left from failed tests
        cls.remove_populated_preferences()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up after test case
        """
        # Remove any preferences created for the test
        cls.remove_populated_preferences()

        reset_django_settings()

    def populate_user_preferences(self, total):
        """
        Push user preferences
        """
        for num in xrange(total):
            self.profile_server.set_user_data(
                self.user,
                self.APP,
                {'test_data': 'test/data/{0}'.format(num)},
            )

    @classmethod
    def remove_populated_preferences(cls):
        """
        Remove all populated preferences
        """
        for item in cls.profile_server.get_user_data(cls.user, key=cls.APP):
            cls.profile_server.delete_user_data(item['id'])

    def test_get_user_details(self):
        """
        Test getting user details
        """
        details = self.profile_server.details(self.test_email)

        assert_in('username', details)
        assert_in('first_name', details)
        assert_in('last_name', details)
        assert_in('email', details)
        assert_equals(self.test_email, details['email'])
        assert_in('phone', details)
        assert_in('mobile', details)
        assert_in('subscribed', details)
        assert_in('subscriptions', details)
        assert_in('state', details)
        assert_in('groups', details)
        assert_in('resource_uri', details)

    def test_get_user_preferences(self):
        """
        Test getting more than 20 user preference records
        """
        total = 30

        # Populate user preferences
        self.populate_user_preferences(total)

        # Get user preferences
        user_preferences = self.profile_server.get_user_data(self.user,
                                                             key=self.APP)

        assert_equals(total, len(user_preferences))
