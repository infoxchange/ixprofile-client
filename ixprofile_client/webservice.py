"""
Web service to interact with the profile server user records
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import json
import warnings
from logging import getLogger
from urllib.parse import urljoin  # pylint:disable=import-error

import requests

from django.conf import settings
from django.utils.http import urlencode

from ixprofile_client import exceptions


LOG = getLogger(__name__)


class UserWebService(object):
    """
    Web service to interact with the profile server user records
    """

    USER_LIST_URI = "/api/v2/user/"
    USER_URI = "/api/v2/user/%s/"
    GROUP_URI = "/api/v2/group/%s/"

    register_email_template = None
    register_email_subject = None

    def _list_uri(self, **kwargs):
        """
        The URL for the user list.
        """
        if kwargs:
            query_string = '?' + urlencode(kwargs, doseq=True)
        else:
            query_string = ''

        return urljoin(self.profile_server, self.USER_LIST_URI) + query_string

    def _detail_uri(self, username):
        """
        The URL for the user details.
        """
        return urljoin(self.profile_server, self.USER_URI % username)

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
            auth=(
                settings.PROFILE_SERVER_KEY,
                settings.PROFILE_SERVER_SECRET
            ),
            verify=settings.SSL_CA_FILE,
            **kwargs
        )

    def __init__(self):
        """
        Create a new instance of a Web service.
        """
        self.profile_server = settings.PROFILE_SERVER

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
        response = self._request('PATCH', self._detail_uri(user.username),
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

    def details(self, email=None, username=None):
        """
        Get the user details from the profile server.

        Either 'username' or 'email' must be explicitly passed as kwargs,
        so the old calls passing 'username' stop working.
        """

        warnings.warn("Please user 'find_by_username' or 'find_by_email'.",
                      DeprecationWarning)

        if username is not None and email is not None:
            raise ValueError("Exactly one of 'username' or 'email' must be "
                             "specified in the arguments.")

        if username is not None:
            return self.find_by_username(username)
        elif email is not None:
            return self.find_by_email(email)
        else:
            raise ValueError("Exactly one of 'username' or 'email' must be "
                             "specified in the arguments.")

    def find_by_username(self, username):
        """
        Find a user by username.
        """

        response = self._request('GET', self._detail_uri(username))
        if response.status_code == requests.codes.not_found:
            return None

        self._raise_for_failure(response)
        return response.json()

    def find_by_email(self, email):
        """
        Find a user by email.

        If the email address is not unique, raise a EmailNotUnique exception.
        """

        users = self.list(email=email)
        count = users['meta']['total_count']
        if count == 0:
            return None
        elif count > 1:
            raise exceptions.EmailNotUnique(None, email)

        return users['objects'][0]

    def list(self, **kwargs):
        """
        List all the users subscribed to the application.

        Kwargs are turned into a query string and
        sent to profile server's /user/ endpoint.
        """

        response = self._request('GET', self._list_uri(**kwargs))
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

        if user.username:
            data['username'] = user.username

        if self.register_email_template is not None:
            data['email_template'] = self.register_email_template
        if self.register_email_subject is not None:
            data['email_subject'] = self.register_email_subject
        response = self._request('POST', self._list_uri(),
                                 data=json.dumps(data))
        self._raise_for_failure(response)
        return response.json()

    def connect(self, user, commit=True):
        """
        Ensure a user with given user's email exists on the profile server,
        update the details as needed and save the user if commit is True.
        """
        if user.username:
            details = self.find_by_username(user.username)
        else:
            details = self.find_by_email(user.email)
            if details:
                user.username = details['username']

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

    def reset_password(self, user):
        """
        Send the user a password reset email.
        """

        response = self._request(
            'POST',
            urljoin(self._detail_uri(user.username), 'reset-password/'),
        )
        self._raise_for_failure(response)

    def get_group(self, group, **kwargs):
        """
        Request the users in a profile server group

        Profile server groups are typically referred to by a URI resource name
        i.e. http://iss3/service/1234/ -- the names are considered meaningful
        to the applications.
        """

        url = urljoin(self.profile_server,
                      self.GROUP_URI % group)

        LOG.debug("Requesting users for group '%s'", url)

        response = self._request('GET', url,
                                 params=kwargs)

        # pylint:disable=no-member
        # Instance of 'LookupDict' has no 'not_found' member
        if response.status_code == requests.codes.not_found:
            return []
        else:
            self._raise_for_failure(response)
            return response.json()['users']

    def add_group(self, user, group):
        """
        Add a user to the named group
        """
        return self.add_groups(user, [group])

    def add_groups(self, user, groups):
        """
        Add a user to the list of named groups
        """
        data = {
            'groups': list(
                set(self.find_by_username(user.username)['groups'] + groups)
            ),
        }

        response = self._request('PATCH',
                                 self._detail_uri(user.username),
                                 data=json.dumps(data))
        self._raise_for_failure(response)

        return response.json()['groups']

    def remove_group(self, user, group):
        """
        Remove a user from the named group
        """
        return self.remove_groups(user, [group])

    def remove_groups(self, user, groups):
        """
        Remove a user from multiple groups
        """

        current_groups = set(self.find_by_username(user.username)['groups'])

        data = {
            'groups': list(current_groups - set(groups)),
        }

        response = self._request('PATCH',
                                 self._detail_uri(user.username),
                                 data=json.dumps(data))
        self._raise_for_failure(response)

        return response.json()['groups']

    def set_details(self, user, **details):
        """
        Set the details for the user
        """

        # If `subscribed' is not set but we are changing the status of
        # the current app, `subscribed' must be set
        if 'subscribed' not in details and 'subscriptions' in details \
                and settings.PROFILE_SERVER_KEY in details['subscriptions']:
            details['subscribed'] = \
                details['subscriptions'][settings.PROFILE_SERVER_KEY]

        response = self._request('PATCH',
                                 self._detail_uri(user.username),
                                 data=json.dumps(details))
        self._raise_for_failure(response)

        return response.json()

    def get_user_data(self, user, key=None):
        """
        Get the user data for the user, including an optional key
        """

        url = self._detail_uri(user.username) + 'preferences/'
        params = {'limit': 0}

        if key:
            params['type'] = key

        response = self._request('GET', url, params=params)

        try:
            data = response.json()['objects']
        except (ValueError, KeyError):
            return []

        return data

    def set_user_data(self, user, key, value):
        """
        Set user data for the user. This data is stored as a key-value
        pair inside the profile server
        """

        data = {
            'user': self.USER_URI % user.username,
            'type': key,
            'data': value,
        }

        response = self._request('POST',
                                 urljoin(self.profile_server,
                                         '/api/v2/user-preference/'),
                                 data=json.dumps(data))
        self._raise_for_failure(response)

        return response.json()

    def delete_user_data(self, id_):
        """
        Delete user data by id
        """

        response = self._request('DELETE',
                                 urljoin(self.profile_server,
                                         '/api/v2/user-preference/%d/' % id_))
        self._raise_for_failure(response)


# pylint:disable=invalid-name
profile_server = UserWebService()
