"""
Route configuration for the IX Profile client
"""

from django.conf.urls import include, url
from django.views.generic import TemplateView

# pylint:disable=invalid-name,no-value-for-parameter
# The name 'urlpatterns' is a part of the API
# 'cls' is a bogus parameter
urlpatterns = [
    url(r'', include('social_django.urls', namespace='social')),
    url(r'^ixlogin/unbox/', TemplateView.as_view(template_name='unbox.html')),
]
