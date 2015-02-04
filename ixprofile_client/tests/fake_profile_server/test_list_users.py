"""
Test listing users in the fake profile server.
"""

from __future__ import absolute_import

from operator import itemgetter

from ...util import leave_only_keys
from . import FakeProfileServerTestCase


class RemoveGroupsTestCase(FakeProfileServerTestCase):
    """
    Test listing users in the fake profile server.
    """

    maxDiff = None

    def setUp(self):
        """
        Add adminable app and some users to the mock.
        """

        super(RemoveGroupsTestCase, self).setUp()
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
            'subscriptions': {
                'another_app': True,
                'unrelated': True,
            },
        })

        # Completely unrelated
        self.mock_ps.register({
            'email': 'norman@yahoo.uk',
            'subscriptions': {
                'unrelated': True,
            },
        })

    def test_list_users(self):
        """
        Test listing the users subscribed to the application.
        """

        users = sorted(map(
            leave_only_keys('email', 'subscribed', 'subscriptions'),
            self.mock_ps.list()
        ), key=itemgetter('email'))

        self.assertEqual(users, [
            {
                'email': 'bob@gov.gl',
                'subscribed': True,
                'subscriptions': {
                    'mock_app': True,
                    'another_app': False,
                },
            },
            {
                'email': 'corvax@gov.gl',
                'subscribed': True,
                'subscriptions': {
                    'mock_app': True,
                    'another_app': True,
                },
            },
            {
                'email': 'muzzy@stell.ar',
                'subscribed': False,
                'subscriptions': {
                    'mock_app': False,
                    'another_app': True,
                },
            },
        ])
