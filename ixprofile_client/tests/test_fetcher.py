"""
Tests for utility functions
"""
from __future__ import unicode_literals

from unittest import TestCase

from django.conf import settings
from mock import MagicMock, patch
from openid.fetchers import HTTPResponse
from requests import Response

from ..fetchers import ProxyFetcher


class TestProxyFetcher(TestCase):
    """
    Tests for the `ProxyFetcher` class.
    """

    def test_performs_get_requests(self):
        """
        Test `ProxyFetcher` performs GET requests.
        """
        fetcher = ProxyFetcher()

        with patch('requests.get') as mock_get:
            fetcher.fetch('http://nowhere.com')

        mock_get.assert_called()

    def test_request_goes_to_specified_url(self):
        """
        Test `ProxyFetcher` fetches the correct URL.
        """
        fetcher = ProxyFetcher()
        url = 'http://nowhere.com'

        with patch('requests.get') as mock_get:
            fetcher.fetch(url)

        args, _ = mock_get.call_args
        self.assertIn(url, args)

    def test_post_when_body_provided(self):
        """
        Test `ProxyFetcher` performs a POST when a body is provided.
        """

        fetcher = ProxyFetcher()

        with patch('requests.post') as mock_post:
            fetcher.fetch('http://nowhere.com', body={'foo': 'bar'})

        mock_post.assert_called()

    def test_headers_on_post(self):
        """
        Test `ProxyFetcher` sets the Content-Type header on POST requests.
        """

        fetcher = ProxyFetcher()

        with patch('requests.post') as mock_post:
            fetcher.fetch('http://nowhere.com', body={'foo': 'bar'})

        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['Content-Type'], 'application/json')

    def test_sets_auth(self):
        """
        Test `ProxyFetcher` sets `auth` for external requests.
        """

        expected_auth = (
            settings.PROFILE_SERVER_KEY,
            settings.PROFILE_SERVER_SECRET
        )
        fetcher = ProxyFetcher()

        with patch('requests.get') as mock_get:
            fetcher.fetch('http://nowhere.com')

        _, kwargs = mock_get.call_args
        self.assertEqual(expected_auth, kwargs['auth'])

    def test_sets_body(self):
        """
        Test `ProxyFetcher` sets `body` for external requests.
        """

        fetcher = ProxyFetcher()

        with patch('requests.post') as mock_post:
            fetcher.fetch('http://nowhere.com', body={'foo': 'bar'})

        _, kwargs = mock_post.call_args
        self.assertEqual({'foo': 'bar'}, kwargs['body'])

    def test_sets_verify(self):
        """
        Test `ProxyFetcher` specifies the SSL certificate file.
        """
        fetcher = ProxyFetcher()

        with patch('requests.get') as mock_get:
            fetcher.fetch('http://nowhere.com')

        _, kwargs = mock_get.call_args
        self.assertEqual(settings.SSL_CA_FILE, kwargs['verify'])

    def test_sets_proxies(self):
        """
        Test `ProxyFetcher` uses the proxies for external requests.
        """

        fetcher = ProxyFetcher()

        with patch('requests.get') as mock_get:
            fetcher.fetch('http://nowhere.com')

        _, kwargs = mock_get.call_args
        self.assertEqual(settings.PROXIES, kwargs['proxies'])

    def test_returns_httpresponse(self):
        """
        Test `fetch` returns an `HTTPResponse`.
        """
        fetcher = ProxyFetcher()

        with patch('requests.get') as mock_get:
            # Prevent requests from actually sending an HTTP request.
            mock_get.return_value = Response()

            response = fetcher.fetch('http://nowhere.com')

        self.assertIsInstance(response, HTTPResponse)

    def test_response_properties(self):
        """
        Test the `HTTPResponse` has the expected properties.

        `fetch` should return a `openid.fetchers.HTTPResponse` with properties
        based on the content of the response.
        """
        fake_response = Response()
        fake_response.url = 'http://nowhere.com'
        fake_response.status_code = 200
        fake_response.headers = {'Fake-Header': 'fakeit'}
        # pylint:disable=protected-access
        fake_response._content = 'Fake content'

        fetcher = ProxyFetcher()

        with patch('requests.get') as mock_get:
            # Return a faked response from `requests.request` so we don't have
            # to hit an external service.
            mock_get = MagicMock
            mock_get.return_value = fake_response

            response = fetcher.fetch('http://nowhere.com')

        self.assertEqual(fake_response.url, response.final_url)
        self.assertEqual(fake_response.status_code, response.status)
        self.assertEqual(fake_response.headers, response.headers)
        self.assertEqual(fake_response.content, response.body)
