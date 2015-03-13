"""
Miscelanneous utilities.
"""
from operator import itemgetter


def leave_only_keys(*keys):
    """
    A function to leave only the specified keys in the dictionary.
    """

    def filtered(dict_):
        """
        Filter a dictionary by keys.
        """
        return {
            key: dict_[key]
            for key in keys
            if key in dict_
        }

    return filtered


def multi_key_sort(items, order_by, getter=itemgetter):
    """
    Sort a list of dicts objects by multiple keys bidirectionally.

    To sort dicts, use itemgetter for the getter function

    Allows sorting in the same way as order_by on a Django queryset
    """
    comparers = []

    for key in order_by:
        if key.startswith('-'):
            field = key[1:]
            polarity = -1
        else:
            field = key
            polarity = 1

        comparers.append((getter(field), polarity))

    def comparer(left, right):
        """
        Comparison function to compare two dicts or objects given a set of
        polarities
        """
        for func, polarity in comparers:
            result = cmp(func(left), func(right))
            if result:
                return polarity * result

        return 0

    return sorted(items, cmp=comparer)
