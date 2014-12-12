"""
A django-socialauth based client for the IX Profile server
"""

from django.apps import AppConfig
from django.conf import settings


class IXProfileClientConfig(AppConfig):
    """
    Application configuration for the IX Profile client.
    """

    name = 'ixprofile_client'

    def ready(self):
        """
        Configure the social auth pipeline.
        """

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


# pylint:disable=invalid-name
default_app_config = 'ixprofile_client.IXProfileClientConfig'
# pylint:enable=invalid-name
