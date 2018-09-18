"""
An OpenID URL fetcher respecting the settings.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import inspect
import sys

PY3 = sys.version_info >= (3, 0)

# Important: python3-open uses urllib.request, whereas (python2) openid uses
# urllib2. You cannot use the compatibility layer here.
if PY3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

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
        if PY3 or 'cafile' in inspect.getargspec(urlopen).args:
            from django.conf import settings
            if hasattr(settings, 'SSL_CA_FILE'):
                kwargs['cafile'] = settings.SSL_CA_FILE

                if hasattr(settings, 'PROFILE_SERVER') and \
                        '.office.infoxchange.net.au' in settings.PROFILE_SERVER:
                    kwargs['cafile'] = '/etc/ssl/certs/ca-certificates.crt'

        return urlopen(*args, **kwargs)
