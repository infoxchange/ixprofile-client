"""
A django-socialauth based client for the IX Profile server
"""

try:
    # Django 1.7+
    from django.apps import AppConfig
except ImportError:
    # Stub for old Django
    AppConfig = object

from django.conf import settings

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'ixprofile_client.pipeline.match_user',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


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
