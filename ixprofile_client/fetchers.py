"""
An OpenID URL fetcher respecting the settings.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import inspect
import urllib.request

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
        if 'cafile' in inspect.getargspec(urllib.request.urlopen).args:
            from django.conf import settings
            if hasattr(settings, 'SSL_CA_FILE'):
                kwargs['cafile'] = settings.SSL_CA_FILE

        return urllib.request.urlopen(*args, **kwargs)
