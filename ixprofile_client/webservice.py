"""
Web service to interact with the profile server user records
"""

from django.conf import settings

from ixdjango.utils import flatten_auth_header
from ixwsauth import auth

import json

import requests
from requests.auth import AuthBase


class OAuth(AuthBase):
    """
    OAuth-like authorization for requests library.
    """
    def __init__(self, key, secret):
        """
        Initialize the key and secret for the AuthManager
        """
        self.key = key
        self.secret = lambda: secret

    def __call__(self, request):
        """
        Sign the request.
        """
        payload = {
            'method': request.method,
            'url': request.url,
            'params': {},
        }
        auth_man = auth.AuthManager()
        signed_payload = auth_man.oauth_signed_payload(self, payload)
        request.headers['Authorization'] = flatten_auth_header(
            signed_payload['headers']['Authorization'],
            'OAuth'
        )
        return request


class UserWebService(object):
    """
    Web service to interact with the profile server user records
    """

    USER_LIST_URI = "api/user/"
    USER_URI = "api/user/%s/"

    def _list_uri(self):
        """
        The URL for the user list.
        """
        return self.profile_server + self.USER_LIST_URI

    def _detail_uri(self, email):
        """
        The URL for the user details.
        """
        return self.profile_server + self.USER_URI % email

    def __init__(self):
        """
        Create a new instance of a Web service.
        """
        self.profile_server = settings.PROFILE_SERVER
        self.auth = OAuth(
            settings.PROFILE_SERVER_KEY,
            settings.PROFILE_SERVER_SECRET
        )

    def _set_subscription_status(self, user, status):
        """
        Set the subscription status of a user.
        """
        data = {'subscribed': status}
        response = requests.patch(
            self._detail_uri(user.email),
            auth=self.auth,
            data=json.dumps(data),
            verify=settings.SSL_CA_FILE,
        )
        response.raise_for_status()

    def subscribe(self, user):
        """
        Subscribe the user to the current application on the profile server
        """
        self._set_subscription_status(user, True)

    def unsubscribe(self, user):
        """
        Unsubscribe the user from the current application on the profile server
        """
        self._set_subscription_status(user, False)

    def details(self, email):
        """
        Get the user details from the profile server
        """
        response = requests.get(
            self._detail_uri(email),
            auth=self.auth,
            verify=settings.SSL_CA_FILE,
        )
        # pylint:disable=E1101
        # Instance of 'LookupDict' has no 'not_found' member
        if response.status_code == requests.codes.not_found:
            return None
        response.raise_for_status()
        return response.json()

    def register(self, user):
        """
        Register a new user on the profile server
        """
        data = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        response = requests.post(
            self._list_uri(),
            auth=self.auth,
            data=json.dumps(data),
            verify=settings.SSL_CA_FILE,
        )
        response.raise_for_status()
