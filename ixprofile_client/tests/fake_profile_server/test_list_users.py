"""
Test listing users in the fake profile server.
"""

from __future__ import absolute_import

from operator import itemgetter

from ...util import leave_only_keys
from . import FakeProfileServerTestCase


class ListUserTestCase(FakeProfileServerTestCase):
    """
    Test listing users in the fake profile server.
    """

    maxDiff = None

    def setUp(self):
        """
        Add adminable app and some users to the mock.
        """

        super(ListUserTestCase, self).setUp()
        self.mock_ps.adminable_apps = ('another_app',)

        # Subscribed user
        self.mock_ps.register({
            'email': 'bob@gov.gl',
            'subscribed': True,
        })

        # Subscribed to multiple apps
        self.mock_ps.register({
            'email': 'corvax@gov.gl',
            'subscribed': True,
            'subscriptions': {
                'mock_app': True,
                'another_app': True,
                'unrelated': True,
            },
        })

        # Subscribed to another app
        self.mock_ps.register({
            'email': 'muzzy@stell.ar',
            'subscribed': False,
            'subscriptions': {
                'another_app': True,
                'unrelated': True,
            },
        })

        # Completely unrelated
        self.mock_ps.register({
            'email': 'norman@yahoo.uk',
            'subscribed': False,
            'subscriptions': {
                'unrelated': True,
            },
        })

    def test_list_users(self):
        """
        Test listing the users subscribed to the application.
        """

        filter_interesting = \
            leave_only_keys('email', 'subscribed', 'subscriptions',
                            'ever_subscribed_websites')

        users = self.mock_ps.list()

        self.assertEqual(users['meta']['total_count'], 2)

        user_list = sorted(
            map(filter_interesting, users['objects']),
            key=itemgetter('email'))

        # For stable comparison
        for user in user_list:
            user['ever_subscribed_websites'].sort()

        self.assertEqual(user_list, [
            {
                'email': 'bob@gov.gl',
                'subscribed': True,
                'subscriptions': {
                    'mock_app': True,
                    'another_app': False,
                },
                'ever_subscribed_websites': ['mock_app']
            },
            {
                'email': 'corvax@gov.gl',
                'subscribed': True,
                'subscriptions': {
                    'mock_app': True,
                    'another_app': True,
                },
                'ever_subscribed_websites': [
                    'another_app',
                    'mock_app',
                    'unrelated',
                ]
            },
        ])
