"""
An OpenID URL fetcher respecting the settings.
"""

from __future__ import absolute_import, unicode_literals

import inspect
import sys
import warnings

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen  # pylint:disable=import-error

from openid.fetchers import HTTPFetcher, HTTPResponse, Urllib2Fetcher
import requests
PY3 = sys.version_info >= (3, 0)


class SettingsAwareFetcher(Urllib2Fetcher):
    """
    An URL fetcher for python-openid to verify the certificates against
    SSL_CA_FILE in Django settings.
    """

    def __init__(self, *args, **kwargs):
        """
        Warn users about this class being deprecated.
        """
        # `SettingsAwareFetcher` will be removed in version 2.1
        warnings.warn(("`SettingsAwareFetcher` is deprecated. "
                       "Use `ProxyFetcher` instead."),
                      DeprecationWarning)
        super(SettingsAwareFetcher, self).__init__(*args, **kwargs)

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

        return urlopen(*args, **kwargs)


class ProxyFetcher(HTTPFetcher):
    """
    An `HTTPFetcher` which uses the proxies specifed by settings.PROXIES.
    """

    def fetch(self, url, body=None, headers=None):
        """
        Return the response from the Open ID provider.
        """
        headers = headers or {}
        headers.setdefault('Content-Type', 'application/json')

        if body is None:
            response = self._get(url, headers)
        else:
            response = self._post(url, body, headers)

        return HTTPResponse(
            final_url=response.url,
            status=response.status_code,
            headers=response.headers,
            body=response.content,
        )

    @property
    def defaults(self):
        """
        Return the default keyword arguments for the request.
        """
        from django.conf import settings
        return {
            'auth': (
                settings.PROFILE_SERVER_KEY,
                settings.PROFILE_SERVER_SECRET
            ),
            'verify': settings.SSL_CA_FILE,
            'proxies': settings.PROXIES,
        }

    def _get(self, url, headers):
        """
        Perform a GET request and return the response.
        """
        return requests.get(url, headers=headers, **self.defaults)

    def _post(self, url, body, headers):
        """
        Perform a POST request and return the response.
        """
        return requests.post(url, body=body, headers=headers, **self.defaults)
