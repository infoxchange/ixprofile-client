"""
Route configuration for the IX Profile client
"""
from django.conf.urls import include, patterns, url

from ixprofile_client.views import login_start

# pylint:disable=C0103
# The name 'urlpatterns' is a part of the API
urlpatterns = patterns(
    '',
    url(r'', include('social_auth.urls')),
    url(r'^login-start$', login_start, name='ixprofile-start-login'),
)
