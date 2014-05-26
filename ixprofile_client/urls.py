"""
Route configuration for the IX Profile client
"""

from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView

# pylint:disable=invalid-name,no-value-for-parameter
# The name 'urlpatterns' is a part of the API
# 'cls' is a bogus parameter
urlpatterns = patterns(
    '',
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^ixlogin/unbox/', TemplateView.as_view(template_name='unbox.html')),
)
