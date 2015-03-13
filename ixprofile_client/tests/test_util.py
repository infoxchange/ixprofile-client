"""
Tests for utility functions
"""
from unittest import TestCase

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
            ('zzz', 'bbb'),
            ('ccc', 'fff'),
            ('hhh', 'bbb'),
            ('ddd', 'ggg'),
            ('aaa', 'kkk'),
        ]:
            self.data.append({'first_name': first, 'last_name': last})

    def _sort(self, *fields):
        """
        Return first name/last name tuples sorted by the given fields
        """
        data = multi_key_sort(self.data, fields)

        return [(user['first_name'], user['last_name']) for user in data]

    def test_sort_first_name(self):
        """
        Test sorting by first name
        """
        data = self._sort('first_name')

        self.assertEqual(data, [
            ('aaa', 'kkk'),
            ('ccc', 'fff'),
            ('ddd', 'ggg'),
            ('hhh', 'bbb'),
            ('zzz', 'bbb'),
        ])

    def test_sort_reverse_first_name(self):
        """
        Test sorting by first name reversed
        """
        data = self._sort('-first_name')

        self.assertEqual(data, [
            ('zzz', 'bbb'),
            ('hhh', 'bbb'),
            ('ddd', 'ggg'),
            ('ccc', 'fff'),
            ('aaa', 'kkk'),
        ])

    def test_sort_last_and_first_names(self):
        """
        Test sorting by last and first name
        """
        data = self._sort('last_name', 'first_name')

        self.assertEqual(data, [
            ('hhh', 'bbb'),
            ('zzz', 'bbb'),
            ('ccc', 'fff'),
            ('ddd', 'ggg'),
            ('aaa', 'kkk'),
        ])
