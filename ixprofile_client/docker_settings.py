"""
Standard config for loading profiles server settings from Docker
"""

import inspect
import urllib2
import os

from furl import furl

from openid.fetchers import Urllib2Fetcher

PROFILE_SERVER = None
PROFILE_SERVER_KEY = None
PROFILE_SERVER_SECRET = None

if 'PROFILE_SERVER_URL' in os.environ:
    # Set key and secret, then remove from profiles URL
    # pylint:disable=invalid-name
    _profile_server_url = furl(os.environ.get('PROFILE_SERVER_URL'))
    PROFILE_SERVER_KEY = _profile_server_url.username
    PROFILE_SERVER_SECRET = _profile_server_url.password

    _profile_server_url.remove(username=True, password=True)
    PROFILE_SERVER = _profile_server_url.url


class SettingsAwareFetcher(Urllib2Fetcher):
    """
    An URL fetcher for python-openid to verify the certificates against
    SSL_CA_FILE in Django settings.
    """

    @staticmethod
    def urlopen(*args, **kwargs):
        """
        Provide urlopen with the trusted certificate path.
        """

        # Old versions of urllib2 cannot verify certificates
        if 'cafile' in inspect.getargspec(urllib2.urlopen).args:
            from django.conf import settings
            kwargs['cafile'] = settings.SSL_CA_FILE

        return urllib2.urlopen(*args, **kwargs)


# Make OpenID module trust the proper certificates
from openid.fetchers import setDefaultFetcher
setDefaultFetcher(SettingsAwareFetcher())
