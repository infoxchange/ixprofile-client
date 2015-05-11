"""
Unit tests
"""

import django

from django.conf import settings

# Configure Django as required by some of the Gherkin steps
settings.configure(
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }},
    PROFILE_SERVER='dummy_server',
    PROFILE_SERVER_KEY='mock_app',
    PROFILE_SERVER_SECRET='dummy_secret',
    SSL_CA_FILE=None,
    DEBUG=True)
django.setup()  # pylint:disable=no-member
