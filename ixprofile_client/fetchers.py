"""
An OpenID URL fetcher respecting the settings.
"""

from __future__ import absolute_import, unicode_literals

import inspect
import sys

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen  # pylint:disable=import-error

from openid.fetchers import Urllib2Fetcher

PY3 = sys.version_info >= (3, 0)


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
        # pylint:disable=deprecated-method
        if PY3 or 'cafile' in inspect.getargspec(urlopen).args:
            from django.conf import settings
            if hasattr(settings, 'SSL_CA_FILE'):
                kwargs['cafile'] = settings.SSL_CA_FILE
                if hasattr(settings, 'PROFILE_SERVER') and \
                        '.office.infoxchange.net.au' in settings.PROFILE_SERVER:
                    kwargs['cafile'] = '/etc/ssl/certs/ca-certificates.crt'

        return urlopen(*args, **kwargs)
