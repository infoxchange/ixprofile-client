"""
Miscellaneous utilities.
"""
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


def multi_key_sort(items, order_by, functions=None, getter=itemgetter):
    """
    Sort a list of dicts or objects by multiple keys bidirectionally.

    To sort dicts, use `itemgetter' for the getter function.
    To sort objects, use `attrgetter'.

    Pass in a dict of `functions' for advanced sorting rules (see
    `function_chain').

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


def function_chain(inner_func, *outer_funcs):
    """
    Create a single unary function from multiple unary functions
    """
    if not outer_funcs:
        return inner_func

    outer_func = function_chain(*outer_funcs)

    return lambda *args, **kwargs: outer_func(inner_func(*args, **kwargs))


def sort_case_insensitive(field, getter=itemgetter):
    """
    Create a function chain to get the lowercase version of a field
    """
    return function_chain(getter(field), methodcaller('lower'))
