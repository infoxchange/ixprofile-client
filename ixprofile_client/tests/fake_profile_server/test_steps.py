"""
Test Lettuce Steps
"""

from __future__ import absolute_import

import os

from lettuce.core import Feature
from mock import MagicMock
# pylint:disable=no-name-in-module
from nose.tools import assert_equals

from ... import steps
from ... import webservice

# pylint:disable=invalid-name
original_profile_server = webservice.profile_server

feature1_filename = os.path.join(os.path.dirname(__file__),
                                 'test_feature.feature')
with open(feature1_filename) as feature1_file:
    FEATURE1 = feature1_file.read()


class TestLettuceSteps(object):
    """
    Test Lettuce Steps
    """

    default_details = {
        'email': '',
        'first_name': '',
        'last_name': '',
        'mobile': '',
        'phone': '',
        'state': '',
        'subscribed': False,
        'subscriptions': {'mock_app': False},
        'username': '',
        'groups': [],
    }

    expected_users = {
        u'zoidberg@px.ea': {
            'subscribed': True,
            'first_name': u'John',
            'last_name': u'Zoidberg',
            'phone': 1468023579,
        },
        u'hmcdoogal@px.ea': {
            'subscribed': False,
            'first_name': u'Hattie',
            'last_name': u'McDoogal',
            'phone': u'',
        },
        u'acalculon@px.ea': {
            'subscribed': True,
            'first_name': u'Antonio',
            'last_name': u'Calculon',
            'phone': u'0292538800',
        },
        u'mendoza@mcog.fr': {
            'subscribed': True,
            'first_name': u'Mendoza',
            'last_name': u'Unknown',
            'phone': u'',
            'subscriptions': {
                u'golden-condor': True,
                u'solaris': True,
            },
        }
    }

    def details_for(self, email):
        """
        Return the expected details for the given email
        """
        new_details = dict(self.default_details.items() +
                           self.expected_users[email].items())
        new_details['email'] = email

        if new_details['subscribed']:
            new_details['subscriptions']['mock_app'] = True

        return new_details

    # pylint:disable=invalid-name
    def setUp(self):
        """
        This method is run before _each_ test
        """
        self.mock_step = MagicMock()
        self.mock_scenario = MagicMock()
        self.mock_outline = MagicMock()

    # pylint:disable=invalid-name
    def test_initialise_real_profile_server(self):
        """
        When scenario contains tags @integration @profiles, the real profile
        server is used
        """
        self.mock_scenario = MagicMock(tags=['integration', 'profiles'])

        steps.initialise_profile_server(self.mock_scenario,
                                        self.mock_outline,
                                        (self.mock_step,))

        assert webservice.profile_server == original_profile_server

    # pylint:disable=invalid-name
    def test_initialise_mock_profile_server(self):
        """
        When scenario doesn't contain tags @integration @profiles, the mocked
        profile server is used
        """
        steps.initialise_profile_server(self.mock_scenario,
                                        self.mock_outline,
                                        (self.mock_step,))

        assert webservice.profile_server != original_profile_server

    def test_add_profile_server_users(self):
        """
        Test adding users to the fake profile server
        """
        Feature.from_string(FEATURE1).run()

        for email in self.expected_users.keys():
            stored = webservice.profile_server.details(email)

            assert_equals(self.details_for(email), stored)
