"""
Unit tests
"""
import django
import unittest

from django.conf import settings

# Configure Django it is required for initializing the profile server object
settings.configure(
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }},
    PROFILE_SERVER='dummy_server',
    PROFILE_SERVER_KEY='dummy_key',
    PROFILE_SERVER_SECRET='dummy_secret',
    DEBUG=True)
django.setup()

from ixprofile_client import webservice
from ixprofile_client.steps import (initialise_profile_server,
                                    RealProfileServer,
                                    restore_real_profile_server)


class MockPSTestCase(unittest.TestCase):
    """
    Base class for tests that requires a mock Profile Server
    """
    # pylint:disable=invalid-name
    def setUp(self):
        """
        This method is run before _each_ test
        """
        initialise_profile_server()

        # Check that we are using the mock profile server
        assert webservice.profile_server != RealProfileServer,\
            "Using the real Profile Server"

    def tearDown(self):
        """
        Restore real profile server
        """
        restore_real_profile_server()
