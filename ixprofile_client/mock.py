"""
Utilities for testing applications using the profile server.
"""

import json

from hashlib import sha256

from django.conf import settings
from django.utils.timezone import now

import requests

from ixprofile_client import webservice
from ixprofile_client.exceptions import EmailNotUnique, ProfileServerFailure

from .util import multi_key_sort, sort_case_insensitive


SORT_RULES = {
    'first_name': sort_case_insensitive,
    'last_name': sort_case_insensitive,
}

RealProfileServer = webservice.profile_server  # pylint:disable=invalid-name


class MockProfileServer(webservice.UserWebService):
    """
    A mock profile server
    """

    adminable_apps = ()
    not_unique_emails = []

    # pylint:disable=super-init-not-called
    def __init__(self):
        # Try to get the application name from the settings
        try:
            self.app = settings.PROFILE_SERVER_KEY
        except AttributeError:
            self.app = 'mock_app'

        self.users = {}
        self.user_data = {}

    @classmethod
    def _user_to_dict(cls, user):
        """
        Convert either a Django user or a dict to internal representation.

        In case of a dict, extra keys (like 'subscriptions') that are not
        present on normal Users will be preserved.
        """

        details_fields = {
            'email': (True, ''),
            'first_name': (True, ''),
            'last_name': (True, ''),
            'username': (True, ''),
            'phone': (False, ''),
            'mobile': (False, ''),
            'state': (False, ''),
            'date_joined': (True, now()),
            'last_login': (True, None),
            'is_locked': (False, False),
            'groups': (False, []),
            'subscribed': (False, True),
            'subscriptions': (False, {}),
            'ever_subscribed_websites': (False, []),
        }

        if isinstance(user, dict):
            return {
                key: user.get(key, default)
                for key, (_, default) in details_fields.items()
            }
        else:
            return {
                key: getattr(user, key) if real else default
                for key, (real, default) in details_fields.items()
            }

    def find_by_email(self, email):
        """
        Find a user's details by email.
        Raise an error on duplicate emails.
        """

        if email in self.not_unique_emails:
            raise EmailNotUnique(None, email)

        return super(MockProfileServer, self).find_by_email(email)

    def find_by_username(self, username):
        """
        Find a user's details by username.
        """

        return self._user_details(self.users.get(username, None))

    def _visible_apps(self):
        """
        All the applications visible by this key.
        """

        return (self.app,) + tuple(self.adminable_apps)

    def _user_details(self, user):
        """
        Return the user details in the same format as the real API.
        """

        if user is None:
            return None

        user = user.copy()
        user['subscriptions'] = {
            app: user['subscriptions'].get(app, False)
            for app in self._visible_apps()
        }
        user['subscribed'] = user['subscriptions'][self.app]

        # Date fields are strings in JSON
        for field in ('date_joined', 'last_login'):
            if user[field]:
                user[field] = user[field].isoformat()

        self._update_ever_subscribed_websites(user)
        return user

    def _update_ever_subscribed_websites(self, user):
        """
        Ensure ever_subscribed_websites is up to date.
        """
        # Add any active subscriptions.
        active_subscriptions = [app for app in user['subscriptions']
                                if user['subscriptions'][app]]
        user['ever_subscribed_websites'] += active_subscriptions

        # Get rid of any duplicate entries.
        user['ever_subscribed_websites'] = \
            list(set(user['ever_subscribed_websites']))

    def _check_username(self, user):
        """
        Raise an error if the username of a given user record is already taken
        by another user.
        """

        user = self._user_to_dict(user)

        if not user.get('username'):
            # Don't check empty usernames
            return

        username = user['username']
        exclude_email = user['email']

        if username in self.users and \
                self.users[username]['email'] != exclude_email:
            # Imitate the ValidationError dict returned by the real profile
            # server.
            self._raise_failure({
                'user': {
                    'username': [
                        "This username is already taken.",
                    ],
                },
            })

    def _dummy_response(self, content=''):
        """
        Make a dummy requests.Response with the specifying content.
        """

        response = requests.Response()
        # pylint:disable=protected-access
        response._content = content.encode()
        response.status_code = 400

        return response

    def _raise_failure(self, error_json):
        """
        Raise a ProfileServerFailure exception with the supplied error message.
        """

        raise ProfileServerFailure(
            self._dummy_response(json.dumps(error_json)))

    def list(self, **kwargs):  # pylint:disable=too-complex
        """
        List all the users subscribed to the application.
        """

        self.last_list_kwargs = kwargs.copy()

        user_list = [
            self._user_details(user)
            for user in self.users.values()
        ]

        # Default sorting in PS is by ID, do stable sorting by email instead
        # Email is more meaningful than hashed usernames
        sort_by = kwargs.pop('order_by', 'email')

        if not isinstance(sort_by, list):
            sort_by = [sort_by]

        user_list = multi_key_sort(user_list, sort_by, SORT_RULES)

        # Filter only subscribed/adminable users, unless searching by email
        if 'email' not in kwargs:
            if kwargs.pop('include_adminable', False):
                interesting_apps = self._visible_apps()
            else:
                interesting_apps = (self.app,)

            was_subscribed = kwargs.pop('was_subscribed', False)
            if was_subscribed:
                user_list = [
                    user for user in user_list
                    if any([app in user['ever_subscribed_websites']
                            for app in interesting_apps]) and
                    not any(user['subscriptions'].get(app, False)
                            for app in interesting_apps)
                ]
            else:
                user_list = [
                    user for user in user_list
                    if any(user['subscriptions'].get(app, False)
                           for app in interesting_apps)
                ]

        searchable_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

        if 'q' in kwargs:
            q_lookup = kwargs.pop('q').lower()
            user_list = [
                user for user in user_list
                if any(
                    q_lookup in user[field].lower()
                    for field in searchable_fields
                )
            ]

        for field in searchable_fields:
            if field in kwargs:
                value = kwargs.pop(field).lower()
                user_list = [
                    user for user in user_list
                    if user[field].lower() == value
                ]

        # Save total count before chopping the list
        total_count = len(user_list)

        offset = int(kwargs.pop('offset', 0))
        user_list = user_list[offset:]

        # Limit is implied to be 20 if omitted
        limit = int(kwargs.pop('limit', 20))
        if limit > 0:
            user_list = user_list[:limit]

        if kwargs:
            # Unrecognised parameters. They might be supported by the real
            # profile server, but raise an exception rather than silently
            # doing the wrong thing.
            raise ValueError(
                "Unrecognised parameters in list call: {0}".format(
                    kwargs.keys()
                )
            )

        return {
            'meta': {
                'limit': limit,
                'next': None,
                'offset': offset,
                'previous': None,
                'total_count': total_count,
            },
            'objects': user_list,
        }

    @staticmethod
    def _generate_username(user):
        """
        Generate a username for a user.
        """

        hash_base = user['email'].lower().encode()
        return 'sha256:' + sha256(hash_base).hexdigest()[:23]

    def register(self, user):
        """
        Register a new user
        """
        user = self._user_to_dict(user)

        self._check_username(user)

        username = user.get('username')
        if not username:
            username = user['username'] = self._generate_username(user)

        # Remove 'subscribed', all the necessary information is in
        # 'subscriptions'
        user['subscriptions'][self.app] = user.pop('subscribed')
        self._update_ever_subscribed_websites(user)
        self.users[username] = user

        return user

    def _set_subscription(self, user, state):
        """
        Update the subscription status to state
        """

        username = self._user_to_dict(user)['username']

        self.users[username]['subscriptions'][self.app] = state

    def unsubscribe(self, user):
        """
        Register an unsubscription request
        """
        self._set_subscription(user, False)

    def subscribe(self, user):
        """
        Register a subscription request
        """

        self._set_subscription(user, True)

    def reset_password(self, user):
        """
        Mock sending the user a password reset email.

        The user's email is saved on the object, so it can be checked later in
        a test.
        """

        if user.username not in self.users:
            self._raise_failure("Unknown user.")
        self.last_reset_password = user.username

    def add_group(self, user, group):
        """
        Add a user to a group
        """
        return self.add_groups(user, [group])

    def add_groups(self, user, groups):
        """
        Add a user to a list of groups
        """
        details = self._user_to_dict(user)
        username = details['username']

        user = self.users.setdefault(username, details)
        user['groups'] = list(set(user['groups'] + groups))

        return user['groups']

    def remove_group(self, user, group):
        """
        Remove a user from a group
        """
        return self.remove_groups(user, [group])

    def remove_groups(self, user, groups):
        """
        Remove a user from multiple groups
        """
        details = self._user_to_dict(user)
        username = details['username']

        user = self.users[username]
        user['groups'] = list(set(user.get('groups', [])) - set(groups))

        return user['groups']

    def get_group(self, group, **kwargs):
        """
        Get the users for the groups

        FIXME: Kwargs are ignored
        """
        return [user for user in self.users.values()
                if group in user['groups']]

    def set_details(self, user, **kwargs):
        """
        Set details for the user
        """

        username = self._user_to_dict(user)['username']

        # If `subscribed' is not set but we are changing the status of
        # the current app, `subscribed' must be set
        if 'subscribed' not in kwargs and 'subscriptions' in kwargs \
                and self.app in kwargs['subscriptions']:
            kwargs['subscribed'] = kwargs['subscriptions'][self.app]

        # 'subscribed' overrides 'subscriptions'
        try:
            subscribed = kwargs.pop('subscribed')
            kwargs.setdefault('subscriptions', {})[self.app] = subscribed
        except KeyError:
            pass

        for key in kwargs:
            if key not in self.users[username]:
                self._raise_failure("Invalid user key: {0}".format(key))

        try:
            self.users[username]['subscriptions'].update(
                kwargs.pop('subscriptions'))
        except KeyError:
            pass

        self._check_username(kwargs)

        self.users[username].update(kwargs)

        return self.users[username]

    def set_user_data(self, user, key, value):
        """
        Set user data for user
        """

        data = {
            'type': key,
            'data': value,
        }
        data['id'] = id(data)

        details = self._user_to_dict(user)
        self.user_data.setdefault(details['username'], []).append(data)

    def delete_user_data(self, id_):
        """
        Delete user data by id
        """

        for user_data in self.user_data.values():
            for data in user_data:
                if data['id'] == id_:
                    user_data.remove(data)

    def get_user_data(self, user, key=None):
        """
        Get user data for the user
        """

        details = self._user_to_dict(user)
        try:
            data = self.user_data[details['username']]

            if key:
                data = [record
                        for record in data
                        if record['type'] == key]

            return data

        except KeyError:
            return []


def mock_profile_server():
    """
    Switch the profile server to the mocked one.
    """

    webservice.profile_server = MockProfileServer()


def unmock_profile_server():
    """
    Switch the profile server to the real one.
    """

    webservice.profile_server = RealProfileServer
