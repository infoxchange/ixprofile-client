"""
django-socialauth pipeline part for IX Profile server
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from social.exceptions import AuthFailed

import re

from ixprofile_client.webservice import UserWebService


webservice = UserWebService()  # pylint:disable=invalid-name


# pylint:disable=W0613
# Unused arguments are a part of the API
def match_user(strategy, details, response, uid, *args, **kwargs):
    """
    Given an OpenID from the profile server, find a user with the same
    username.
    """

    # check the user's subscription status
    email = details['email']
    ws_details = webservice.details(email)

    if not ws_details['subscribed']:
        return HttpResponseRedirect("/no-user")

    match = re.match('^%sid/u/(.+)$' % settings.PROFILE_SERVER, uid)

    if match:
        username = match.group(1)
        try:
            # user is known to us
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
