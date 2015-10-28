"""Basic Enum data structure.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Enum -- Basic enumerated value object.
    :class EnumInt -- Enum with int values instead of str.

"""

from core.dotdict import ImmutableDotDict


class Enum(ImmutableDotDict):
    """ Simple class for generating enumerated sets of constants.

    Init Parameters:
        *args: One or more strings. These will be the literal
            enum values, as well as the property names.

    Usage:
        Values = Enum('One', 'Two', 'Horse')
        repr(Values.One) #-> "'One'"
        repr(Values['Two']) #-> "'Two'"
        repr(Values) #-> "['Horse', 'One', 'Two']"
    """

    def __init__(self, *args):
        """Enum init.

        :param args: str,... -- Enum literal values / prop names.
        """
        if len(args) == 1 and type(args[0]) is dict:
            d = args[0]
        else:
            d = {}
            for arg in args:
                d[arg] = arg
        super(Enum, self).__init__(d)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return str(tuple(self))


class EnumInt(Enum):
    """ C-style enum with int values, rather than str.

    Init Parameters:
        *args: One or more strings. These will be the property
            names. Values assigned are in order of supplied
            arguments in ascending order.

    Usage:
        Values = Enum('One', 'Two', 'Horse')
        repr(Values.One) #-> "1"
        repr(Values['Horse']) #-> "3"
        repr(Values) #-> "['One', 'Two', 'Horse']"
    """

    def __init__(self, *args):
        """Enum init.

        :param args: str,... -- Enum literal values / prop names.
        """
        d = dict(zip(args, range(1, len(args) + 1)))
        self._ordered_args = args
        super(Enum, self).__init__(d)

    def __repr__(self):
        return str(self._ordered_args)
