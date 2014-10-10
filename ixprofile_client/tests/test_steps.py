"""
Test Lettuce Steps
"""

import django

from django.conf import settings
from lettuce.core import Feature
from mock import MagicMock
# pylint:disable=no-name-in-module
from nose.tools import assert_equals

# Configure Django it is required by some of the lettuce steps
settings.configure(
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }},
    PROFILE_SERVER='dummy_server',
    PROFILE_SERVER_KEY='dummy_key',
    PROFILE_SERVER_SECRET='dummy_secret',
    DEBUG=True)
django.setup()

from ixprofile_client import steps
from ixprofile_client import webservice

# pylint:disable=invalid-name
original_profile_server = webservice.profile_server


FEATURE1 = """
Feature: Test fake profile server
  Scenario: Initialize profile server
    Given I have users in the fake profile server:
      | email           | subscribed | first_name | last_name | phone      | subscriptions          | # nopep8
      | zoidberg@px.ea  | true       | John       | Zoidberg  | 1468023579 |                        | # nopep8
      | hmcdoogal@px.ea | false      | Hattie     | McDoogal  |            |                        | # nopep8
      | acalculon@px.ea | true       | Antonio    | Calculon  | 0292538800 |                        | # nopep8
      | mendoza@mcog.fr | true       | Mendoza    | Unknown   |            | golden-condor,solaris  | # nopep8
"""


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
