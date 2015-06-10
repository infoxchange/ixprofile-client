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
import socket
import urlparse
from time import time

from django.conf import settings
from django.contrib.auth import get_backends, login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.timezone import now
from lettuce import before, step, world
from lettuce import django as lettuce_django
from lettuce.django.steps.models import hashes_data
# pylint:disable=no-name-in-module
from nose.tools import assert_equals, assert_in, assert_not_in
from selenium.webdriver.support.ui import WebDriverWait
from social.exceptions import AuthException
import social.apps.django_app.views

from ixprofile_client import webservice
from ixprofile_client.mock import (
    mock_profile_server,
    MockProfileServer,
    unmock_profile_server,
)


def site_url(url):
    """
    Determine the server URL.
    """

    base_url = 'http://%s' % socket.gethostname()

    if lettuce_django.server.port is not 80:
        base_url += ':%d' % lettuce_django.server.port

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


@step(r'Fake profile server user "([^"]+)" has preferences:')
def set_preferences(self, email):
    """
    Set preferences for a mock profile server user
    And the fake profile server user "happy@example.com" has preferences:
        | favourite | {"entity_id": 102, "name": "One"}      |
        | favourite | {"entity_id": 103, "something": "Two"} |
    """

    assert isinstance(webservice.profile_server, MockProfileServer)

    user = User(
        username=webservice.profile_server.find_by_email(email)['username']
    )

    for preference, value in self.table:
        value = json.loads(value)
        webservice.profile_server.set_user_data(user, preference, value)


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
        if 'email' in row:
            key = 'email'
            func = webservice.profile_server.find_by_email
        else:
            key = 'username'
            func = webservice.profile_server.find_by_username

        details = func(row[key])
        assert not details, "User present: %s" % row[key]


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
        user, last_login=user.last_login)

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


@before.each_example  # pylint:disable=no-member
# pylint:disable= unused-argument
def initialise_profile_server(scenario, *args):
    """
    If the feature isn't a profile server integration feature, then mock
    the profile server
    """

    tags = scenario.tags or []

    if 'integration' in tags and 'profiles' in tags:
        unmock_profile_server()
        auth_handler.use_auth = auth_handler.real_auth
    else:
        mock_profile_server()
        auth_handler.use_auth = auth_handler.fake_no_auth


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

    actual_kwargs = webservice.profile_server.last_list_kwargs.copy()

    for kwargs in (expected_kwargs, actual_kwargs):
        try:
            kwargs['order_by'] = [
                order_by.strip()
                for order_by
                in kwargs['order_by'].split(',')
            ]
        except (KeyError, AttributeError):
            pass

    assert_equals(expected_kwargs, actual_kwargs)


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
