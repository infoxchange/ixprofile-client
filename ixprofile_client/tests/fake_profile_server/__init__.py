"""
Unit tests against the fake profile server
"""

from __future__ import absolute_import

from unittest import TestCase

from ...steps import MockProfileServer


class FakeProfileServerTestCase(TestCase):
    """
    Base class for testing the fake profile server.
    """

    def setUp(self):
        """
        Initialise the test case
        """
        self.mock_ps = MockProfileServer()
