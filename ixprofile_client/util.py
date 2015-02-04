"""
Miscelanneous utilities.
"""


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
