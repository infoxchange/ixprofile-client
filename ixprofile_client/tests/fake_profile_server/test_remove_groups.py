"""
Test removing groups from users in the fake profile server.
"""

from __future__ import absolute_import

# pylint:disable=no-name-in-module
from nose.tools import assert_not_in

from . import FakeProfileServerTestCase


class RemoveGroupsTestCase(FakeProfileServerTestCase):
    """
    Test removing groups from users.
    """

    def test_remove_groups(self):
        """
        Test the user is removed from all the groups in the list
        """

        calculon = {
            'email': 'acalculon@all.my.circuits',
        }
        fry = {
            'email': 'philip.j.fry@planet.express',
        }

        # Create the groups by adding users to groups
        self.mock_ps.add_groups(calculon, ['group1', 'group2'])
        self.mock_ps.add_groups(fry, ['group1'])

        # Remove user from a group he doesn't belong to
        self.mock_ps.remove_groups(fry, ['group1', 'group2'])

        users = self.mock_ps.get_group('group1')
        assert_not_in('philip.j.fry@planet.express',
                      [user['email'] for user in users])

        users = self.mock_ps.get_group('group2')
        assert_not_in('philip.j.fry@planet.express',
                      [user['email'] for user in users])
