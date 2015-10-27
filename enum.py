"""Basic Enum data structure.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Enum -- Basic enumerated value object.

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
        d = {}
        for arg in args:
            d[arg] = arg
        super(Enum, self).__init__(d)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return str(list(self))
