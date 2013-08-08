"""
Web service to interact with the profile server user records
"""

from django.conf import settings

from ixdjango.utils import flatten_auth_header
from ixwsauth import auth

import json

import requests
from requests.auth import AuthBase

from ixprofile_client import exceptions


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

    register_email_template = None

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

    @staticmethod
    def _raise_for_failure(response):
        """
        Raise an appropriate exception on a Web service response
        """
        if 400 <= response.status_code < 600:
            raise exceptions.ProfileServerFailure(response)

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
        self._raise_for_failure(response)

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
        elif response.status_code == requests.codes.multiple_choices:
            raise exceptions.EmailNotUnique(email)
        else:
            self._raise_for_failure(response)
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
        if self.register_email_template is not None:
            data['email_template'] = self.register_email_template
        response = requests.post(
            self._list_uri(),
            auth=self.auth,
            data=json.dumps(data),
            verify=settings.SSL_CA_FILE,
        )
        self._raise_for_failure(response)
        return response.json()

    def connect(self, user, commit=True):
        """
        Ensure a user with given user's email exists on the profile server,
        update the details as needed and save the user if commit is True.
        """
        details = self.details(user.email)
        if details is None:
            details = self.register(user)
        else:
            self.subscribe(user)
            user.first_name = details['first_name']
            user.last_name = details['last_name']
        user.username = details['username']
        user.set_password(None)
        if commit:
            user.save()
        return user
