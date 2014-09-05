"""
Test create superuser command
"""

from mock import MagicMock

from ixprofile_client import webservice
from ixprofile_client.management.commands import createsuperuser
from ixprofile_client.tests import MockPSTestCase


class TestCreateSuperUser(MockPSTestCase):
    """
    Test create superuser command
    """

    # pylint:disable=invalid-name
    def setUp(self):
        """
        This method is run before _each_ test
        """
        super(TestCreateSuperUser, self).setUp()

        # Mock Django models
        self.original_User = createsuperuser.User
        self.original_Transaction = createsuperuser.transaction

        self.test_user = MagicMock()
        self.test_user.dict = {}

        # pylint:disable= unused-argument
        def getitem(name, *args):
            """
            Make the mock act as a dictionary
            """
            return self.test_user.dict.get(name, '')

        self.test_user.get = getitem

        def get_or_create(email):
            """
            Create a user object
            """
            self.test_user.dict['email'] = email

            return (self.test_user, True)

        # Mock User Model
        manager = MagicMock()
        manager.get_or_create = get_or_create
        createsuperuser.User = MagicMock(objects=manager)
        createsuperuser.transaction = MagicMock()

    # pylint:disable=invalid-name
    def test_create_superuser(self):
        """
        Create a superuser using the command line
        """
        # Check that the user is not created
        assert self.test_user.is_active is not True
        assert self.test_user.is_staff is not True
        assert self.test_user.is_superuser is not True

        command = createsuperuser.Command()
        command.stdout = MagicMock()

        email = 'superuser@test.com'
        command.handle(interactive=False, email=email)

        # Check that the user was created in the profile server
        user_details = webservice.profile_server.details(email)
        assert user_details is not None
        assert user_details['subscribed'] is True

        # Check that the user was created in the database correctly
        assert self.test_user.is_active is True
        assert self.test_user.is_staff is True
        assert self.test_user.is_superuser is True
