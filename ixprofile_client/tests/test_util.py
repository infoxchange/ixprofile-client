"""
Tests for utility functions
"""
from unittest import TestCase

from ixprofile_client.mock import SORT_RULES
from ixprofile_client.util import multi_key_sort


class MultiKeySortTestCase(TestCase):
    """
    Tests for the multi key sort function
    """

    def setUp(self):
        """
        Generate some test data
        """
        self.data = []

        for first, last in [
            ('Homer', 'Simpson'),
            ('Marge', 'Simpson'),
            ('Bart', 'Simpson'),
            ('Lisa', 'SIMPSON'),
            ('Maggie', 'Simpson'),
        ]:
            self.data.append({'first_name': first, 'last_name': last})

    def _sort(self, *fields):
        """
        Return first name/last name tuples sorted by the given fields
        """
        data = multi_key_sort(self.data, fields, SORT_RULES)

        return [(user['first_name'], user['last_name']) for user in data]

    def test_sort_first_name(self):
        """
        Test sorting by first name
        """
        data = self._sort('first_name')

        self.assertEqual(data, [
            ('Bart', 'Simpson'),
            ('Homer', 'Simpson'),
            ('Lisa', 'SIMPSON'),
            ('Maggie', 'Simpson'),
            ('Marge', 'Simpson'),
        ])

    def test_sort_reverse_first_name(self):
        """
        Test sorting by first name reversed
        """
        data = self._sort('-first_name')

        self.assertEqual(data, [
            ('Marge', 'Simpson'),
            ('Maggie', 'Simpson'),
            ('Lisa', 'SIMPSON'),
            ('Homer', 'Simpson'),
            ('Bart', 'Simpson'),
        ])

    def test_sort_last_and_first_names(self):
        """
        Test sorting by last and first name
        """
        data = self._sort('last_name', 'first_name')

        self.assertEqual(data, [
            ('Bart', 'Simpson'),
            ('Homer', 'Simpson'),
            ('Lisa', 'SIMPSON'),
            ('Maggie', 'Simpson'),
            ('Marge', 'Simpson'),
        ])
