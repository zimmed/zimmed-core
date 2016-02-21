"""Custom exception types.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class InitError
    :class StateError

"""


class InitError(StandardError):
    """Designates error with class initialization process."""
    pass


class StateError(RuntimeError):
    """Errors pertaining to an object's state at runtime."""
    pass


class LogicError(RuntimeError):
    """Errors pertaining to the desired logic-path of certain behavior."""
    pass
