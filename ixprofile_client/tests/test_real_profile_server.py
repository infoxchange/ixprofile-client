"""
Test Lettuce Steps
"""

from __future__ import absolute_import

import os

from django.conf import settings
from mock import MagicMock
# pylint:disable=no-name-in-module
from nose.tools import assert_equals, assert_true

from ..docker_settings import (
    PROFILE_SERVER,
    PROFILE_SERVER_KEY,
    PROFILE_SERVER_SECRET,
)

# pylint:disable=protected-access
setattr(settings._wrapped, 'PROFILE_SERVER', PROFILE_SERVER)
setattr(settings._wrapped, 'PROFILE_SERVER_KEY', PROFILE_SERVER_KEY)
setattr(settings._wrapped, 'PROFILE_SERVER_SECRET', PROFILE_SERVER_SECRET)
setattr(settings._wrapped, 'SSL_CA_FILE', os.environ.get('SSL_CA_FILE'))

# This should go after django settings
from ..webservice import profile_server


class TestRealProfileServer(object):
    """
    Test real profile server, these tests only run when the ENV variables are
    set:
    PROFILE_SERVER_URL=https://KEY:SECRET@profile.server
    SSL_CA_FILE=path/to/ssl_ca_certificate.crt
    """

    APP = 'ixprofile_client_test'
    test_email = 'bashful@infoxchange.net.au'

    def mock_user(self, email):
        """
        Return a mock user
        """
        return MagicMock(email=email)

    def populate_user_preferences(self, user, total):
        """
        Push user preferences
        """
        for num in xrange(total):
            profile_server.set_user_data(
                user,
                self.APP,
                {'test_data': 'test/data/{0}'.format(num)},
            )

    def remove_populated_preferences(self, user):
        """
        Remove all populated preferences
        """
        for item in profile_server.get_user_data(user, key=self.APP):
            profile_server.delete_user_data(item['id'])

    def test_get_user_details(self):
        """
        Test getting user details
        """
        if PROFILE_SERVER != 'None':
            details = profile_server.details(self.test_email)

            assert_true('username' in details)
            assert_true('first_name' in details)
            assert_true('last_name' in details)
            assert_true('email' in details)
            assert_equals(self.test_email, details['email'])
            assert_true('phone' in details)
            assert_true('mobile' in details)
            assert_true('subscribed' in details)
            assert_true('subscriptions' in details)
            assert_true('state' in details)
            assert_true('groups' in details)
            assert_true('resource_uri' in details)

        # Mark the test as OK if the profile server is not configured
        assert True

    def test_get_user_preferences(self):
        """
        Test getting more than 20 user preference records
        """
        total = 30

        if PROFILE_SERVER != 'None':
            user = self.mock_user(self.test_email)

            # Remove any preference left from failed tests
            self.remove_populated_preferences(user)

            # Populate user preferences
            self.populate_user_preferences(user, total)

            # Get user preferences
            user_preferences = profile_server.get_user_data(user,
                                                            key=self.APP)

            assert_equals(total, len(user_preferences))

            # Remove test user preferences
            self.remove_populated_preferences(user)

        # Mark the test as OK if the profile server is not configured
        assert True
