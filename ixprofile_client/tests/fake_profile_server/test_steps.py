"""
Test Lettuce Steps
"""

from __future__ import absolute_import

import os

from django.utils.timezone import now
from aloe.testing import FeatureTest
from freezegun import freeze_time
from mock import MagicMock
# pylint:disable=no-name-in-module
from nose.tools import assert_equals

from ... import steps
from ... import webservice

# pylint:disable=invalid-name
original_profile_server = webservice.profile_server

feature1_filename = os.path.join(os.path.dirname(__file__),
                                 'test_features',
                                 'test_feature.feature')


@freeze_time('2015-01-01')
class TestLettuceSteps(FeatureTest):
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
        'last_login': None,
        'is_locked': False,
        'subscribed': False,
        'subscriptions': {'mock_app': False},
        'ever_subscribed_websites': [],
        'username': '',
        'groups': [],
    }

    expected_users = {
        u'zoidberg@px.ea': {
            'subscribed': True,
            'subscriptions': {
                'mock_app': True,
                'golden-condor': False,
                'solaris': False,
            },
            'ever_subscribed_websites': ['mock_app'],
            'username': 'sha256:a5d8d5f520acfd109e2bd83',
            'first_name': u'John',
            'last_name': u'Zoidberg',
            'phone': 1468023579,
        },
        u'hmcdoogal@px.ea': {
            'subscribed': False,
            'subscriptions': {
                'mock_app': False,
                'golden-condor': False,
                'solaris': False,
            },
            'ever_subscribed_websites': [],
            'username': 'sha256:ef205ea3e9e71a3a46e2118',
            'first_name': u'Hattie',
            'last_name': u'McDoogal',
            'phone': u'',
        },
        u'acalculon@px.ea': {
            'subscribed': True,
            'subscriptions': {
                'mock_app': True,
                'golden-condor': False,
                'solaris': False,
            },
            'ever_subscribed_websites': ['mock_app'],
            'username': 'sha256:7365214e537b3669cc13012',
            'first_name': u'Antonio',
            'last_name': u'Calculon',
            'phone': u'0292538800',
        },
        u'mendoza@mcog.fr': {
            'subscribed': True,
            'username': 'sha256:2284980b3e797138d378ad1',
            'first_name': u'Mendoza',
            'last_name': u'Unknown',
            'phone': u'',
            'subscriptions': {
                u'golden-condor': True,
                u'solaris': True,
            },
            'ever_subscribed_websites': [
                'golden-condor',
                'mock_app',
                'solaris',
            ],
        }
    }

    def details_for(self, email):
        """
        Return the expected details for the given email
        """
        new_details = {}
        new_details.update(self.default_details)
        new_details.update(self.expected_users[email])
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

        self.default_details['date_joined'] = now().isoformat()

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

        self.assert_feature_success(feature1_filename)

        webservice.profile_server.adminable_apps = (
            'golden-condor',
            'solaris',
        )

        for email in self.expected_users.keys():
            stored = webservice.profile_server.find_by_email(email)

            # For stable comparison
            stored['ever_subscribed_websites'].sort()

            assert_equals(self.details_for(email), stored)
