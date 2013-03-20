"""
Overrides for django.contrib.auth.models.User
"""

from django.contrib.auth.models import User

from hashlib import sha256


def hash_email(email):
    """
    Hash the user's email to generate a username
    """
    return sha256(email.lower()).hexdigest()[:30]


User.__unicode__ = lambda x: x.email
