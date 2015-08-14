"""
A django-socialauth based client for the IX Profile server
"""

from django.conf import settings

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.social_user',
    'ixprofile_client.pipeline.match_user',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

try:
    # Django 1.7+
    from django.apps import AppConfig
except ImportError:
    settings.SOCIAL_AUTH_PIPELINE = SOCIAL_AUTH_PIPELINE


class IXProfileClientConfig(AppConfig):
    """
    Application configuration for the IX Profile client.
    """

    name = 'ixprofile_client'

    def ready(self):
        """
        Configure the social auth pipeline.
        """

        settings.SOCIAL_AUTH_PIPELINE = SOCIAL_AUTH_PIPELINE


# pylint:disable=invalid-name
default_app_config = 'ixprofile_client.IXProfileClientConfig'
# pylint:enable=invalid-name
