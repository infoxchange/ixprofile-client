"""
Views for the profile server client.
"""
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


# pylint:disable=W0613
# Unused argument is a part of the API
def login_start(request):
    """
    Redirect the user to the IX Profile server
    """
    redirect = reverse('socialauth_begin', kwargs={'backend': 'ixprofile'})
    return HttpResponseRedirect(redirect)
