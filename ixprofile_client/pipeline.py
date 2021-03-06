"""
django-socialauth pipeline part for IX Profile server
"""

# pylint:disable=redefined-builtin,unused-wildcard-import,wrong-import-position
from __future__ import absolute_import, unicode_literals
from future import standard_library
standard_library.install_aliases()
from future.builtins import *
# pylint:enable=redefined-builtin,unused-wildcard-import

import re
from urllib.parse import unquote, urlparse  # pylint:disable=import-error

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from social_core.exceptions import AuthFailed

import ixprofile_client.webservice
# pylint:enable=wrong-import-position


# pylint:disable=unused-argument
# Unused arguments are a part of the API
def match_user(strategy, details, response, uid, *args, **kwargs):
    """
    Given an OpenID from the profile server, find a user with the same
    username.
    """

    # Check whether the OpenID is coming from the expected server
    profile_server = urlparse(settings.PROFILE_SERVER)
    user_url = urlparse(uid)

    if profile_server.scheme != user_url.scheme or \
            profile_server.netloc != user_url.netloc:
        raise AuthFailed("User from the wrong server")

    match = re.match('^/id/u/(.+)$', user_url.path)

    if match:
        username = unquote(match.group(1))

        webservice = ixprofile_client.webservice.profile_server
        ws_details = webservice.find_by_username(username)

        # check the user's subscription status
        if not ws_details['subscribed']:
            return HttpResponseRedirect("/no-user")

        try:
            # user is known to us
            # pylint:disable=no-member
            user = User.objects.get(username=username)
            return {
                'username': username,
                'user': user,
            }
        except User.DoesNotExist:
            # there is no user account, but the user is subscribed,
            # pass to create_user to create one
            return {
                'username': username,
            }
    else:
        raise AuthFailed("Could not determine username")
