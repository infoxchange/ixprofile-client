"""
Profile Server lettuce steps

Import these steps in your features/steps/__init__.py file:
    import ixprofile_client.steps

For integration tests refer to integration_example.feature which connect to
the real profile server.

For functional tests refer to functional_example.feature which uses a mocked
profile server.

"""

from __future__ import division

import json
import math
import requests
import socket
import urlparse
from hashlib import sha256
from operator import itemgetter
from time import time

from django.conf import settings
from django.contrib.auth import get_backends, login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.timezone import now
from lettuce import before, step, world
from lettuce.django import server
from lettuce.django.steps.models import hashes_data
# pylint:disable=no-name-in-module
from nose.tools import assert_equals, assert_in, assert_not_in
from selenium.webdriver.support.ui import WebDriverWait
from social.exceptions import AuthException
import social.apps.django_app.views

from ixprofile_client import webservice
from ixprofile_client.exceptions import EmailNotUnique, ProfileServerFailure

# The real profile server, used for integration tests
RealProfileServer = webservice.profile_server  # pylint:disable=invalid-name


def site_url(url):
    """
    Determine the server URL.
    """

    base_url = 'http://%s' % socket.gethostname()

    if server.port is not 80:
        base_url += ':%d' % server.port

    return urlparse.urljoin(base_url, url)


def _visit_url_wrapper(lettuce_step, url):
    """
    Wrapper around the 'I visit ""' step to catch profile server failures
    """
    try:
        lettuce_step.given('I visit "%s"' % url)
    except AuthException:
        # Catch exception when Profile Server is not found
        pass


@step(r'I visit site page "([^"]*)"')
def visit_page(lettuce_step, page):
    """
    Visit a page of the site
    """
    _visit_url_wrapper(lettuce_step, site_url(page))


@step('The app is named "([^"]+)" in the fake profile server')
def set_app_name(self, app_name):
    """
    Set the application name on the fake profile server.
    """

    assert isinstance(webservice.profile_server, MockProfileServer)

    webservice.profile_server.app = app_name


@step('The app administers the following apps? in the fake profile server:')
def set_adminable_apps(self):
    """
    Set adminable_apps on the fake profile server.
    """

    assert isinstance(webservice.profile_server, MockProfileServer)

    webservice.profile_server.adminable_apps = \
        sum((tuple(row) for row in self.table), ())


@step('I have users in the fake profile server')
def add_profile_server_users(self):
    """
    Add users into the mock profile server

    User subscriptions may be supplied as a comma separated string
    """

    assert isinstance(webservice.profile_server, MockProfileServer)

    for row in hashes_data(self):
        row['groups'] = [group.strip()
                         for group in row.get('groups', '').split(',')
                         if group != '']

        subscriptions = {}
        subscription_apps = row.pop('subscriptions', '').split(',')
        if subscription_apps[0]:
            for app in subscription_apps:
                subscriptions[app] = True
            row['subscriptions'] = subscriptions

        webservice.profile_server.register(row)


@step('I have multiple users in the fake profile server with email "([^"]*)"')
def add_nonunique_email(_, email):
    """
    Subsequent to this, find_by_email(email) will throw EmailNotUnique
    """
    webservice.profile_server.not_unique_emails.append(email)


@step(r'The email "([^"]*)" exists in the (?:real|fake) profile server')
def check_profile_server_user(_, email):
    """
    Check that the user exists into the mock or real profile server
    """

    details = webservice.profile_server.find_by_email(email)
    assert details, "User not present: %s" % email


@step(r'I do not have users in the (?:real|fake) profile server')
def no_user_on_profile_server(self):
    """
    Confirm users do not exist in the mock or real profile server
    """

    for row in self.hashes:
        details = webservice.profile_server.find_by_email(row['email'])
        assert not details, "User present: %s" % row['email']


@step(r'The email "([^"]*)" is part of group "([^"]*)" in the (?:real|fake) '
      r'profile server')
def user_in_ps_group(_, email, group):
    """
    Check that the user is part of the profile server group
    """
    users = webservice.profile_server.get_group(group)
    assert_in(email, [user['email'] for user in users])


@step(r'The email "([^"]*)" is not part of group "([^"]*)" in the '
      r'(?:real|fake) profile server')
def user_not_in_ps_group(_, email, group):
    """
    Check that the user is not part of the profile server group
    """
    users = webservice.profile_server.get_group(group)
    assert_not_in(email, [user['email'] for user in users])


@step('I have users in the real profile server')
def confirm_profile_server_users(self):
    """
    Confirm users exist in the profile server
    """

    for row in hashes_data(self):
        details = webservice.profile_server.find_by_email(row['email'])
        assert details, "Could not find user: %s" % row['email']

        # pylint:disable=unexpected-keyword-arg,no-value-for-parameter
        # Pylint doesn't understand metaclasses
        # https://bitbucket.org/logilab/pylint/issue/353
        user = User(username=details['username'],
                    email=details['email'])
        # pylint:enable=unexpected-keyword-arg,no-value-for-parameter

        if row.get('subscribed', True):
            webservice.profile_server.subscribe(user)
        else:
            webservice.profile_server.unsubscribe(user)

        groups = [group.strip()
                  for group in row.get('groups', '').split(',')
                  if group != '']

        webservice.profile_server.remove_groups(user, details['groups'])
        webservice.profile_server.add_groups(user, groups)


@step(r'I log in to the real profile server with username "([^"]*)" and '
      'password "([^"]*)"')
def login_framed_profile_server(_, username, password):
    """
    Log in through the real profile server, login box is inside a frame
    """

    driver = world.browser

    elem = driver.find_element_by_id('login_frame')
    assert elem, "No login frame"

    driver.switch_to_frame(elem)

    def profile_server_ready(driver):
        """
        Check that the profile server is loaded - either the username
        input or the prefilled username are on the page
        """
        return driver.find_elements_by_class_name('change-user-link') \
            or driver.find_element_by_id('id_username').is_displayed()

    # we're using the real, live profile server, let's wait a while
    WebDriverWait(driver, 10).until(profile_server_ready)

    # Maybe they're already logged in
    elems = driver.find_elements_by_class_name('change-user-link')
    if elems:
        elems[0].click()
        WebDriverWait(driver, 10).until(profile_server_ready)

    elem = driver.find_element_by_id('id_username')
    elem.send_keys(username)

    elem = driver.find_element_by_id('id_password')
    elem.send_keys(password)
    elem.submit()

    driver.switch_to_default_content()


real_auth = social.apps.django_app.views.auth  # pylint:disable=invalid-name


class AuthHandler(object):
    """
    A singleton for handling a mocked authentication requests

    This is a singleton because auth_handler.auth() will be cached by
    Django.
    """

    def auth(self, *args, **kwargs):
        """
        This method will be cached by Django, all of the smart stuff happens
        in things we can change
        """

        return self.use_auth(*args, **kwargs)

    def login_as_user(self, user):
        """
        Reset the auth handler to use another time
        """

        backend = get_backends()[0]
        user.backend = '{module}.{klass}'.format(
            module=backend.__module__,
            klass=backend.__class__.__name__)

        self.user = user
        user.last_login = now()

        assert self.use_auth != self.fake_auth
        self.use_auth = self.fake_auth

    def fake_no_auth(self, request, backend):
        """
        A mocked auth that does nothing.
        """

        return HttpResponse("Login form")

    def fake_auth(self, request, backend):
        """
        A mocked auth that logs in as the user I want it to log in as
        """

        # Single use
        self.use_auth = self.fake_no_auth

        login(request, self.user)

        return HttpResponseRedirect(request.GET['next'])

    def real_auth(self, *args, **kwargs):
        """
        The real authentication method
        """

        return real_auth(*args, **kwargs)

    use_auth = fake_auth


auth_handler = AuthHandler()  # pylint:disable=invalid-name
social.apps.django_app.views.auth = auth_handler.auth


@step(r'I logged in with email "([^"]*)" (\d+) minutes? ago')
def create_login_cookie(self, email, minutes):
    """
    Create a login for the given user
    """

    minutes = int(minutes)

    # prepare an authenticated user using the proper backend

    # pylint:disable=no-member
    user, _ = User.objects.get_or_create(email=email)

    # The user won't go through the python-social-auth pipeline,
    # update their details manually
    details = webservice.profile_server.find_by_email(email)
    for detail in ('username', 'first_name', 'last_name'):
        if details.get(detail, None):
            setattr(user, detail, details[detail])
    user.save()

    auth_handler.login_as_user(user)

    webservice.profile_server.set_details(
        user, last_login=user.last_login.isoformat())

    self.given('I visit site page ""')
    self.given('I left my computer for {0} minutes'.format(minutes))


@step(r'I log in with email "([^"]*)" and visit site page "([^"]*)"')
def login_and_visit(self, email, page):
    """
    Login using the given email and then visit the given page
    """
    self.given('I logged in with email "%s" 0 minutes ago' % email)
    self.given('I visit site page "%s"' % page)


@step(r'I left my computer for (\d+) minutes?')
def age_cookie(_, minutes):
    """
    Age the cookie.

    This will not age the user's session in the database, because although
    there is an API for setting a session timeout, it means "expire X
    minutes after last request", thus subsequent browser requests will result
    in the cookie life decreased rather than renewing the session expiry time.

    For example, if a session expiry time is set down to 60 minutes from 120,
    the next request will not bump it back to 120 but instead set the cookie
    life to 60 minutes as well.
    """

    minutes = int(minutes)

    cookie = world.browser.get_cookie(settings.SESSION_COOKIE_NAME)
    if not cookie:
        # Already expired
        return

    expiry = cookie['expiry'] - minutes * 60
    unix_now = int(time())

    # PhantomJS still sends a cookie if it is added with expiry date in the
    # past. Explicitly delete it in that case.
    if expiry > unix_now:
        world.browser.add_cookie({
            'name': cookie['name'],
            'value': cookie['value'],
            'path': '/',
            'expiry': expiry,
        })
    else:
        world.browser.delete_cookie(settings.SESSION_COOKIE_NAME)


@step(r'my cookie expires in (\d+) minutes?')
def check_login_cookie(_, minutes):
    """
    Check the expiry of my login cookie
    """

    cookie = world.browser.get_cookie(settings.SESSION_COOKIE_NAME)
    minutes = int(minutes)

    expiry_time = cookie['expiry'] - int(time())

    assert_equals(math.ceil(expiry_time / 60), minutes)


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
        self.groups = {}

    @classmethod
    def _user_to_dict(cls, user):
        """
        If user is a Django User, convert it to a dict
        """
        details = {}
        obj_type = type(user)
        details_fields = {
            'email': (True, ''),
            'first_name': (True, ''),
            'last_name': (True, ''),
            'username': (True, ''),
            'phone': (False, ''),
            'mobile': (False, ''),
            'state': (False, ''),
            'last_login': (True, None),
            'is_locked': (False, False),
            'groups': (False, []),
            'subscribed': (False, False),
            'subscriptions': (False, {}),
            'ever_subscribed_websites': (False, []),
        }

        for key, (real, default) in details_fields.items():
            if obj_type == User and real:
                details[key] = getattr(user, key)
            elif obj_type != User:
                details[key] = user.get(key, default)

        if not details['username']:
            details['username'] = cls._generate_username(details)

        return details

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

        # Current app should always be included.
        user['ever_subscribed_websites'] += [self.app]

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
        response._content = content
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
        sort_by = kwargs.pop('sort_by', 'email')
        is_descending = sort_by[0] == '-'
        if is_descending:
            sort_by = sort_by[1:]
        user_list.sort(key=itemgetter(sort_by, 'email'))
        if is_descending:
            user_list.reverse()

        # Filter only subscribed/adminable users, unless searching by email
        if 'email' not in kwargs:
            if kwargs.pop('include_adminable', False):
                interesting_apps = self._visible_apps()
            else:
                interesting_apps = (self.app,)

            # TODO: was_subscribed is not supported
            kwargs.pop('was_subscribed', None)

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

        return 'sha256:' + sha256(user['email'].lower()).hexdigest()[:23]

    def register(self, user):
        """
        Register a new user
        """
        user = self._user_to_dict(user)

        self._check_username(user)

        username = user.get('username', self._generate_username(user))

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

        for group in groups:
            self.groups.setdefault(group, []).append(username)

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

        for group in groups:
            try:
                self.groups.setdefault(group, []).remove(username)
            except ValueError:
                pass

        return user['groups']

    def get_group(self, group):
        """
        Get the users for the groups
        """

        return [
            self.find_by_username(username)
            for username in self.groups.get(group, [])
        ]

    def set_details(self, user, **kwargs):
        """
        Set details for the user
        """

        username = self._user_to_dict(user)['username']

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


@before.each_example  # pylint:disable=no-member
# pylint:disable= unused-argument
def initialise_profile_server(scenario, *args):
    """
    If the feature isn't a profile server integration feature, then mock
    the profile server
    """

    tags = scenario.tags or []

    if 'integration' in tags and 'profiles' in tags:
        new_reference = RealProfileServer
        auth_handler.use_auth = auth_handler.real_auth
    else:
        new_reference = MockProfileServer()
        auth_handler.use_auth = auth_handler.fake_no_auth

    webservice.profile_server = new_reference

    # Replace profile server on ixprofile_client admin form
    from ixprofile_client import forms as ixprofile_forms
    ixprofile_forms.profile_server = new_reference


@step(r'I have last invoked the profile server list '
      'with the following kwargs?:')
def verify_last_list_call(self):
    """
    Verify that list() was invoked with the expected kwargs.

    This is used instead of mocking various Profile Server features,
    including pagination, search, filtering and sorting. See docstring of
    list() above.
    """
    assert isinstance(webservice.profile_server, MockProfileServer)

    expected_kwargs = dict((key, value) for (key, value) in self.table)

    assert_equals(expected_kwargs, webservice.profile_server.last_list_kwargs)


@step(r'Password reset is requested for "([^"]+)"')
def verify_password_request(self, email):
    """
    Verify that a password reset email was requested last for the specified
    email.
    """

    assert isinstance(webservice.profile_server, MockProfileServer)

    username = getattr(webservice.profile_server,
                       'last_reset_password',
                       None)

    assert username is not None, \
        "Password reset has been requested."

    assert_equals(
        email,
        webservice.profile_server.find_by_username(username)['email']
    )
