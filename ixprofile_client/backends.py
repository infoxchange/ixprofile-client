"""
Django Social Auth backend for authentication using the IX Profile server
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from urllib.parse import urljoin  # pylint:disable=import-error

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from social.backends import open_id


class IXProfile(open_id.OpenIdAuth):
    """
    A backend for authentication via the IX Profile server
    """
    name = 'ixprofile'

    def openid_url(self):
        """
        The URL of the OpenID server (profile server).

        This is a static return, but returned via a method to allow for
        mocking of settings.PROFILE_SERVER.
        """

        try:
            profile_server = settings.PROFILE_SERVER
        except AttributeError:
            raise ImproperlyConfigured(
                "No profile server URL (PROFILE_SERVER) in settings."
            )

        return urljoin(profile_server, '/id/xrds/')
