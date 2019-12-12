"""
Overrides for django.contrib.auth.models.User
"""

from django.contrib.auth.models import User


User.__str__ = lambda x: x.email
