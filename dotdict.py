"""Dot-notation dictionary data structures.

Used to make dictionaries where keys can be accessed like properties through
dot notation.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class DotDict -- Standard mutable dot-notation dictionary.
    :class ImmutableDotDict -- Dot-notation dictionary that restricts
        any sets (through dot or bracket notation) after initialization.

"""


class DotDict(dict):
    """Dictionary class where keys are accessible as attributes."""
    def __getattr__(self, item):
        try:
            return self[item]
        except:
            raise AttributeError

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            self[key] = value
        elif key in self:
            self[key] = value
        else:
            self.__dict__[key] = value

    def __delattr__(self, item):
        try:
            del self[item]
        except:
            raise AttributeError


class ImmutableDotDict(DotDict):
    """Read-only dot-notation dictionary."""
    def __setattr__(self, key, value):
        if key not in self and hasattr(self, key):
            self.__dict__[key] = value
        else:
            raise ValueError("Cannot assign to immutable object.")

    def __setitem__(self, key, value):
        raise ValueError("Cannot assign to immutable object.")

    def __delattr__(self, item):
        if item not in self and hasattr(self, item):
            del self.__dict__[item]
        else:
            raise AttributeError("Cannot delete from immutable object.")


# ----------------------------------------------------------------------------
__license__ = "TBD"
__copyright__ = "Copyright (c) 2015 David Zimmelman - All Rights Reserved."
__author__ = "David Zimmelman"
__email__ = "zimmed@zimmed.io"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
