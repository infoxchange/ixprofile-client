"""
Test webservice
"""

from __future__ import absolute_import

from mock import MagicMock
# pylint:disable=no-name-in-module
from nose.tools import assert_equals, assert_in

from . import RealProfileServerTestCase


class TestWebservice(RealProfileServerTestCase):
    """
    Test webservice
    """

    APP = 'ixprofile_client_test'
    test_email = 'bashful@infoxchange.net.au'
    user = MagicMock(email=test_email)

    @classmethod
    def setUpClass(cls):
        """
        Initialise test case
        """
        super(TestWebservice, cls).setUpClass()

        # Remove any preference left from failed tests
        cls.remove_populated_preferences()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up after test case
        """
        # Remove any preferences created for the test
        cls.remove_populated_preferences()

        super(TestWebservice, cls).tearDownClass()

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
