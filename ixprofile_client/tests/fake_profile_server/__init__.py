"""
Unit tests against the fake profile server
"""

from __future__ import absolute_import

from ...steps import MockProfileServer

from unittest import TestCase


class FakeProfileServerTestCase(TestCase):
    """
    Base class for testing the fake profile server.
    """

    def setUp(self):
        """
        Initialise the test case
        """
        self.mock_ps = MockProfileServer()
