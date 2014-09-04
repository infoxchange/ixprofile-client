"""
Standard config for loading profiles server settings from Docker
"""

import os

from furl import furl

# Set key and secret, then remove from profiles URL
# pylint:disable=invalid-name
_profile_server_url = furl(os.environ.get('PROFILE_SERVER_URL'))
PROFILE_SERVER_KEY = _profile_server_url.username
PROFILE_SERVER_SECRET = _profile_server_url.password

_profile_server_url.remove(username=True, password=True)
PROFILE_SERVER = _profile_server_url.url