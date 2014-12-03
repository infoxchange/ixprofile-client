"""
Test Fake Profile Server
"""

from __future__ import absolute_import

# pylint:disable=no-name-in-module
from nose.tools import assert_not_in

from ...steps import MockProfileServer


class TestFakeProfileServer(object):
    """
    Test Fake Profile Server
    """
    mock_ps = None
    users = None
    groups = None

    # pylint:disable=invalid-name
    def setUp(self):
        """
        Initialise the test case
        """
        self.mock_ps = MockProfileServer()
        self.users = {
            'calculon': {
                'email': 'acalculon@all.my.circuits',
            },
            'fry': {
                'email': 'philip.j.fry@planet.express',
            },
        }
        self.groups = [
            'group1',
            'group2',
        ]

    def test_remove_groups(self):
        """
        Test the user is removed from all the groups in the list
        """
        # Create the groups by adding users to groups
        self.mock_ps.add_groups(self.users['calculon'], self.groups)
        self.mock_ps.add_groups(self.users['fry'], [self.groups[1]])

        # Remove user from a group he doesn't belong to
        self.mock_ps.remove_groups(self.users['fry'], self.groups)

        # Check that user is not part of any group
        email = self.users['fry']['email']

        users = self.mock_ps.get_group(self.groups[0])
        assert_not_in(email, [user['email'] for user in users])

        users = self.mock_ps.get_group(self.groups[1])
        assert_not_in(email, [user['email'] for user in users])
