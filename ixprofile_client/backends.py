"""
Django Social Auth backend for authentication using the IX Profile server
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from social_auth import backends
from social_auth.utils import setting


backends.PIPELINE = setting('SOCIAL_AUTH_PIPELINE', (
    'social_auth.backends.pipeline.social.social_auth_user',
    'ixprofile_client.pipeline.match_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
))


if not settings.PROFILE_SERVER:
    raise ImproperlyConfigured(
        "No profile server URL (PROFILE_SERVER) in settings."
    )


class IXProfile(backends.OpenIDBackend):
    """
    An OpenID backend for authenticating via the IX Profile server
    """
    name = 'ixprofile'


class IXProfileAuth(backends.OpenIdAuth):
    """
    A backend for authentication via the IX Profile server
    """
    AUTH_BACKEND = IXProfile

    def openid_url(self):
        return "%s/id/xrds/" % settings.PROFILE_SERVER


BACKENDS = {
    'ixprofile': IXProfileAuth,
}
