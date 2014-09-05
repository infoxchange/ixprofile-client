"""
django-socialauth pipeline part for IX Profile server
"""

import re
import urllib
from urlparse import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from social.exceptions import AuthFailed

from ixprofile_client.webservice import profile_server


# pylint:disable=unused-argument
# Unused arguments are a part of the API
def match_user(strategy, details, response, uid, *args, **kwargs):
    """
    Given an OpenID from the profile server, find a user with the same
    username.
    """

    # check the user's subscription status
    email = details['email']
    ws_details = profile_server.details(email)

    if not ws_details['subscribed']:
        return HttpResponseRedirect('/ixlogin/unbox/no-user')

    profile_server_url = urlparse(settings.PROFILE_SERVER)
    user_url = urlparse(uid)

    if profile_server_url.scheme != user_url.scheme or \
            profile_server_url.netloc != user_url.netloc:
        raise AuthFailed("User from the wrong server")

    match = re.match('^/id/u/(.+)$', user_url.path)

    if match:
        username = urllib.unquote(match.group(1))
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
