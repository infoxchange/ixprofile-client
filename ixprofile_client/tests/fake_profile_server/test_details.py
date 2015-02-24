"""
Test getting user details in the fake profile server.
"""

from __future__ import absolute_import

from ...util import leave_only_keys
from . import FakeProfileServerTestCase


class UserDetailsTestCase(FakeProfileServerTestCase):
    """
    Test listing users in the fake profile server.
    """

    filter_interesting = staticmethod(
        leave_only_keys('email', 'first_name', 'username', 'subscribed'))

    maxDiff = None

    def setUp(self):
        """
        Add adminable app and some users to the mock.
        """

        super(UserDetailsTestCase, self).setUp()

        self.mock_ps.register({
            'email': 'bob@gov.gl',
            'first_name': 'Bob',
        })

        self.mock_ps.register({
            'email': 'corvax@gov.gl',
            'username': 'corvax',
            'first_name': 'Corvax',
        })

    bob_username = 'sha256:8af72939b65cd3089d835d7'

    def test_find_by_email(self):
        """
        Test finding details by email.
        """

        self.assertEqual(
            self.filter_interesting(self.mock_ps.find_by_email('bob@gov.gl')),
            {
                'email': 'bob@gov.gl',
                'username': self.bob_username,
                'first_name': 'Bob',
                'subscribed': True,
            }
        )

        self.assertEqual(
            self.filter_interesting(
                self.mock_ps.find_by_email('corvax@gov.gl')),
            {
                'email': 'corvax@gov.gl',
                'username': 'corvax',
                'first_name': 'Corvax',
                'subscribed': True,
            }
        )

        self.assertEqual(
            self.mock_ps.find_by_email('sylvia@gov.gl'),
            None
        )

        self.assertEqual(
            self.mock_ps.find_by_email(''),
            None
        )

    def test_find_by_username(self):
        """
        Test finding details by username.
        """

        self.assertEqual(
            self.filter_interesting(
                self.mock_ps.find_by_username(self.bob_username)),
            {
                'email': 'bob@gov.gl',
                'username': self.bob_username,
                'first_name': 'Bob',
                'subscribed': True,
            }
        )

        self.assertEqual(
            self.filter_interesting(self.mock_ps.find_by_username('corvax')),
            {
                'email': 'corvax@gov.gl',
                'username': 'corvax',
                'first_name': 'Corvax',
                'subscribed': True,
            }
        )

        self.assertEqual(
            self.mock_ps.find_by_username('sylvia'),
            None
        )

        self.assertEqual(
            self.mock_ps.find_by_username(''),
            None
        )
