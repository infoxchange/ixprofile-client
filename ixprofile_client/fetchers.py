"""
An OpenID URL fetcher respecting the settings.
"""

import inspect
import urllib2

from openid.fetchers import Urllib2Fetcher


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
            if hasattr(settings, 'SSL_CA_FILE'):
                kwargs['cafile'] = settings.SSL_CA_FILE

        return urllib2.urlopen(*args, **kwargs)
