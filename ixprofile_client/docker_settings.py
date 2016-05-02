"""
Standard config for loading profiles server settings from Docker
"""
# pylint:disable=redefined-builtin,unused-wildcard-import
from __future__ import unicode_literals, absolute_import
from future.builtins import *
# pylint:enable=redefined-builtin,unused-wildcard-import

import os

from furl import furl
from openid.fetchers import setDefaultFetcher

from ixprofile_client.fetchers import SettingsAwareFetcher

PROFILE_SERVER = None
PROFILE_SERVER_KEY = None
PROFILE_SERVER_SECRET = None

if 'PROFILE_SERVER_URL' in os.environ:
    # Set key and secret, then remove from profiles URL
    # pylint:disable=invalid-name
    _profile_server_url = furl(os.environ.get('PROFILE_SERVER_URL'))
    PROFILE_SERVER_KEY = str(_profile_server_url.username)
    PROFILE_SERVER_SECRET = str(_profile_server_url.password)

    _profile_server_url.remove(username=True, password=True)
    PROFILE_SERVER = str(_profile_server_url.url)


# Make OpenID module trust the proper certificates
setDefaultFetcher(SettingsAwareFetcher())
