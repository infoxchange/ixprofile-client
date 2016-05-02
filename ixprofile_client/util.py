"""
Miscellaneous utilities.
"""

try:
    reduce
except NameError:
    from functools import reduce  # pylint:disable=redefined-builtin

from functools import total_ordering
from operator import itemgetter, methodcaller


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


@total_ordering
class Negate(object):
    """
    A value that reverses the comparison operators.

    For every two values x and y, if x < y, then Negate(x) > Negate(y) (rules
    for other comparisons are similar).

    Negate values can only be compared to other Negate values.
    """

    def __init__(self, value):
        self.negated = value

    def __lt__(self, another):
        return another.negated < self.negated


def multi_key_sort(items, order_by, functions=None, getter=itemgetter):
    """
    Sort a list of dicts or objects by multiple keys bidirectionally.

    To sort dicts, use `itemgetter' for the getter function.
    To sort objects, use `attrgetter'.

    Pass in a dict of `functions' for advanced sorting rules (see `compose').

    Allows sorting in the same way as order_by on a Django queryset: prefix a
    field with '-' to reverse sorting.
    """
    functions = functions or {}

    comparers = []

    for key in order_by:
        if key.startswith('-'):
            field = key[1:]
            polarity = -1
        else:
            field = key
            polarity = 1

        func = functions.get(key, getter)

        comparers.append((func(field), polarity))

    def multi_key(value):
        """
        Build the comparison tuple for a given value.
        """
        return tuple(
            func(value) if polarity > 0 else Negate(func(value))
            for func, polarity in comparers
        )

    return sorted(items, key=multi_key)


def compose(*functions):
    """
    Create a single unary function from multiple unary functions
    """
    # pylint:disable=undefined-variable
    return reduce(lambda f, g: lambda x: f(g(x)), functions)


def sort_case_insensitive(field, getter=itemgetter):
    """
    Create a function chain to get the lowercase version of a field
    """
    return compose(methodcaller('lower'), getter(field))
