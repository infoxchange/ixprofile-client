"""
Django Social Auth backend for authentication using the IX Profile server
"""

from urlparse import urljoin

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from social.backends import open_id


settings.SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.social_user',
    'ixprofile_client.pipeline.match_user',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)


if not settings.PROFILE_SERVER:
    raise ImproperlyConfigured(
        "No profile server URL (PROFILE_SERVER) in settings."
    )


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

        return urljoin(settings.PROFILE_SERVER, '/id/xrds/')
