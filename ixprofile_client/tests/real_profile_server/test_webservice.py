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
    test_username = 'bashful'
    user = MagicMock(username=test_username)

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
        details = self.profile_server.find_by_username(self.test_username)

        assert_equals(self.test_username, details['username'])
        assert_equals('bashful@infoxchange.net.au', details['email'])
        self.assert_looks_like_a_user(details)

    def assert_looks_like_a_user(self, obj):
        """
        Check that the dictionary looks like a user returned by the profile
        server.
        """

        assert_in('username', obj)
        assert_in('first_name', obj)
        assert_in('last_name', obj)
        assert_in('email', obj)
        assert_in('phone', obj)
        assert_in('mobile', obj)
        assert_in('last_login', obj)
        assert_in('subscribed', obj)
        assert_in('subscriptions', obj)
        assert_in('state', obj)
        assert_in('groups', obj)
        assert_in('resource_uri', obj)

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

    def test_list_users(self):
        """
        Test listing users.
        """

        users = self.profile_server.list()

        self.assertGreater(users['meta']['total_count'], 0)

        for obj in users['objects']:
            self.assert_looks_like_a_user(obj)

    def test_list_users_params(self):
        """
        Test listing users with params
        """
        # pylint:disable=protected-access
        self.assertEquals(
            self.profile_server._list_uri(a='a', b='b'),
            self.profile_server.profile_server + '/api/v2/user/?a=a&b=b'
        )
