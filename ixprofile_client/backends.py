"""
Django Social Auth backend for authentication using the IX Profile server
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from social import pipeline
from social.backends import open_id


pipeline.DEFAULT_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_auth_user',
    'ixprofile_client.pipeline.match_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.update_user_details',
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
        return "%s/id/xrds/" % settings.PROFILE_SERVER
