"""
Test Lettuce Steps
"""

import django

from django.conf import settings
from mock import MagicMock

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


class TestLettuceSteps(object):
    """
    Test Lettuce Steps
    """

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
