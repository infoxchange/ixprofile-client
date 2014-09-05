"""
Test unboxing the frame
"""

from mock import MagicMock

from django.http import HttpResponseRedirect

from ixprofile_client import pipeline
from ixprofile_client import webservice
from ixprofile_client.steps import add_profile_server_user
from ixprofile_client.tests import MockPSTestCase


class TestUnbox(MockPSTestCase):
    """
    Test unboxing the frame
    """

    # pylint:disable=no-self-use
    def test_unsubscribed_user(self):
        """
        When the user is not subscribed, unbox the no-user page
        """
        user = {
            'email': 'user@test.com',
            'subscribed': False,
        }
        add_profile_server_user(user)
        webservice.profile_server.unsubscribe(user)

        strategy = MagicMock()
        details = {'email': user['email']}
        response = MagicMock()
        uid = user['email']

        result = pipeline.match_user(strategy, details, response, uid)

        assert isinstance(result, HttpResponseRedirect)
        assert result.url == '/ixlogin/unbox/no-user'
