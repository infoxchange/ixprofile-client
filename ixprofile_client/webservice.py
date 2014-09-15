"""
Web service to interact with the profile server user records
"""

import json
import urllib
from logging import getLogger
from urlparse import urljoin

import requests
from requests.auth import AuthBase

from django.conf import settings

from ixdjango.utils import flatten_auth_header
from ixwsauth import auth

from ixprofile_client import exceptions


LOG = getLogger(__name__)


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

    USER_LIST_URI = "/api/user/"
    USER_URI = "/api/user/%s/"

    register_email_template = None

    def _list_uri(self):
        """
        The URL for the user list.
        """
        return urljoin(self.profile_server, self.USER_LIST_URI)

    def _detail_uri(self, email):
        """
        The URL for the user details.
        """
        return urljoin(self.profile_server, self.USER_URI % email)

    def _request(self, method, url, **kwargs):
        """
        Make a request to the profile server.
        """

        if method != 'GET':
            kwargs.setdefault('headers', {}).\
                setdefault('Content-Type', 'application/json')

        return requests.request(
            method,
            url,
            auth=self.auth,
            verify=settings.SSL_CA_FILE,
            **kwargs
        )

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
        response = self._request('PATCH', self._detail_uri(user.email),
                                 data=json.dumps(data))
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
        response = self._request('GET', self._detail_uri(email))
        # pylint:disable=no-member
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
        response = self._request('POST', self._list_uri(),
                                 data=json.dumps(data))
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

    def get_group(self, group):
        """
        Request the users in a profile server group

        Profile server groups are typically referred to by a URI resource name
        i.e. http://iss3/service/1234/ -- the names are considered meaningful
        to the applications.
        """

        url = urljoin(self.profile_server, urllib.quote(group))

        LOG.debug("Requesting users for group '%s'", url)

        response = self._request('GET', url)

        # pylint:disable=no-member
        # Instance of 'LookupDict' has no 'not_found' member
        if response.status_code == requests.codes.not_found:
            return []
        else:
            self._raise_for_failure(response)
            return response.json()

# pylint:disable=invalid-name
profile_server = UserWebService()
