"""
Profile Server lettuce steps

Import these steps in your features/steps/__init__.py file:
    import ixprofile_client.steps

For integration tests refer to integration_example.feature which connect to
the real profile server.

For functional tests refer to functional_example.feature which uses a mocked
profile server.

"""

import json
import requests
import socket
import urlparse
from mock import patch

from django.conf import settings
from django.contrib.auth import get_backends, login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect

from selenium.webdriver.support.ui import WebDriverWait

from lettuce import before, step, world
from lettuce.django import server
from lettuce.django.steps.models import hashes_data
from nose.tools import assert_equals  # pylint:disable=no-name-in-module
from social.exceptions import AuthException

from ixprofile_client import webservice

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


@step('I have users in the fake profile server')
def add_profile_server_users(self):
    """
    Add users into the mock profile server
    """

    for row in hashes_data(self):
        groups = []
        if row.get('groups', False):
            groups = row['groups'].split(',')

        webservice.profile_server.register({
            'email': row['email'],
            'subscribed': row['subscribed'],
            'groups': groups,
        })


@step(r'The email "([^"]*)" exists in the (?:real|fake) profile server')
def check_profile_server_user(_, email):
    """
    Check that the user exists into the mock or real profile server
    """

    details = webservice.profile_server.details(email)
    assert details, "User not present: %s" % email


@step(r'I do not have users in the (?:real|fake) profile server')
def no_user_on_profile_server(self):
    """
    Confirm users do not exist in the mock or real profile server
    """

    for row in self.hashes:
        details = webservice.profile_server.details(row['email'])
        assert not details, "User present: %s" % row['email']


@step('I have users in the real profile server')
def confirm_profile_server_users(self):
    """
    Confirm users exist in the profile server
    """

    for row in hashes_data(self):
        details = webservice.profile_server.details(row['email'])
        assert details, "Could not find user: %s" % row['email']

        user = User.objects.create_user(username=details['email'],
                                        email=details['email'])

        if row.get('subscribed', True):
            webservice.profile_server.subscribe(user)
        else:
            webservice.profile_server.unsubscribe(user)

        groups = [group.strip()
                  for group in row.get('groups', '').split(',')
                  if group != '']

        # This should be part of ixprofileclient
        data = {
            'groups': groups,
        }
        # pylint:disable=protected-access
        headers = {'content-type': 'application/json'}
        response = requests.patch(
            webservice.profile_server._detail_uri(user.email),
            auth=webservice.profile_server.auth,
            headers=headers,
            verify=settings.SSL_CA_FILE,
            data=json.dumps(data))
        response.raise_for_status()


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

    # we're using the real, live profile server, let's wait a while
    WebDriverWait(driver, 10).until(
        lambda x: x.find_element_by_id('id_username').is_displayed()
    )

    elem = driver.find_element_by_id('id_username')
    elem.send_keys(username)

    elem = driver.find_element_by_id('id_password')
    elem.send_keys(password)
    elem.submit()

    driver.switch_to_default_content()


def get_session(key=None):
    """
    Get the user's session
    """

    # create the session object
    from django.utils.importlib import import_module

    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(session_key=key)


import social.apps.django_app.views

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

    def login_as_user(self, user, minutes=0):
        """
        Reset the auth handler to use another time
        """

        backend = get_backends()[0]
        user.backend = '{module}.{klass}'.format(
            module=backend.__module__,
            klass=backend.__class__.__name__)

        self.ncalled = 0
        self.user = user
        self.minutes = minutes

    def fake_auth(self, request, backend):
        """
        A mocked auth that logs in as the user I want it to log in as
        """

        if self.ncalled > 0:
            return HttpResponse("Autologin code already called")

        self.ncalled += 1

        login(request, self.user)

        request.session.set_expiry(settings.SESSION_COOKIE_AGE -
                                   self.minutes * 60)
        request.session.save()

        return HttpResponseRedirect(request.GET['next'])

    def real_auth(self, *args, **kwargs):
        """
        The real authentication method
        """

        return real_auth(*args, **kwargs)

    use_auth = fake_auth


auth_handler = AuthHandler()  # pylint:disable=invalid-name


@step(r'I logged in with email "([^"]*)" (\d+) minutes? ago')
def create_login_cookie(self, email, minutes):
    """
    Create a login for the given user
    """

    minutes = int(minutes)

    # prepare an authenticated user using the proper backend
    user = User.objects.get(email=email)  # pylint:disable=no-member
    auth_handler.login_as_user(user, minutes=minutes)

    with patch('social.apps.django_app.views.auth',
               new=auth_handler.auth):
        self.given('I visit site page ""')


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
    Age the cookie
    """

    cookie = world.browser.get_cookie(settings.SESSION_COOKIE_NAME)

    minutes = int(minutes)
    session = get_session(key=cookie['value'])

    session.set_expiry(session.get_expiry_age() - minutes * 60)
    session.save()

    cookie = world.browser.add_cookie({
        'name': settings.SESSION_COOKIE_NAME,
        'value': session.session_key,
    })


@step(r'my cookie expires in (\d+) minutes?')
def check_login_cookie(_, minutes):
    """
    Check the expiry of my login cookie
    """

    minutes = int(minutes)
    session = get_session()

    assert_equals(session.get_expiry_age(), minutes * 60)


class MockProfileServer(webservice.UserWebService):
    """
    A mock profile server
    """

    # pylint:disable=super-init-not-called
    def __init__(self):
        self.users = {}
        self.groups = {}

    @staticmethod
    def _user_to_dict(user):
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
            'groups': (False, []),
            'subscribed': (False, False),
        }

        for key, (real, default) in details_fields.items():
            if obj_type == User and real:
                details[key] = getattr(user, key)
            elif obj_type != User:
                details[key] = user.get(key, default)

        return details

    def details(self, email):
        """
        Return a user's details
        """

        return self.users.get(email, None)

    def register(self, user):
        """
        Register a new user
        """
        details = self._user_to_dict(user)
        self.users[details['email']] = details

        return details

    def unsubscribe(self, user):
        """
        Register an unsubscription request
        """
        details = self._user_to_dict(user)
        self.users[details['email']]['subscribed'] = False

    def subscribe(self, user):
        """
        Register a subscription request
        """
        details = self._user_to_dict(user)
        self.users[details['email']]['subscribed'] = True

    def add_group(self, user, group):
        """
        Add a user to a group
        """

        details = self._user_to_dict(user)
        self.users[details['email']].setdefault('groups', []).append(group)
        self.groups.setdefault(group, []).append(details['email'])

    def get_group(self, group):
        """
        Get the users for the groups
        """

        try:
            users = [self.details(email) for email in self.groups[group]]
        except KeyError:
            users = []

        return users

    def set_details(self, user, **kwargs):
        """
        Set details for the user
        """

        details = self._user_to_dict(user)
        self.users[details['email']].update(kwargs)

        return self.users[details['email']]


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
        auth_handler.use_auth = auth_handler.fake_auth

    webservice.profile_server = new_reference

    # Replace profile server on ixprofile_client admin form
    from ixprofile_client import forms as ixprofile_forms
    ixprofile_forms.profile_server = new_reference
