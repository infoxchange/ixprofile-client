"""
django-socialauth pipeline part for IX Profile server
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

import re


# pylint:disable=W0613
# Unused arguments are a part of the API
def match_user(uid, *args, **kwargs):
    """
    Given an OpenID from the profile server, find a user with the same
    username.
    """
    match = re.match('^%sid/u/(.+)$' % settings.PROFILE_SERVER, uid)
    if match:
        username = match.group(1)
        try:
            user = User.objects.get(username=username)
            return {'user': user}
        except User.DoesNotExist:
            return HttpResponseRedirect("/no-user")
    else:
        return HttpResponseRedirect("/no-user")
