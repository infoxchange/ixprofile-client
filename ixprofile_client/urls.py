"""
Route configuration for the IX Profile client
"""
from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

# pylint:disable=C0103
# The name 'urlpatterns' is a part of the API
urlpatterns = patterns(
    '',
    url(r'', include('social_auth.urls')),
    url(r'^unbox/', TemplateView.as_view(template_name='unbox.html')),
)
