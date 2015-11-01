"""Core decorators.

Potpourri of useful decorators for project.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :callable classproperty -- Decorator for a member function to behave like
        both a classmethod and a property. Accessible like property, but from
        the class, not an instance.
    :callable abstract_class -- Class decorator to designate class as not
        instantiable. Class is an abstract (or meta) class and is only designed
        to be inherited.
"""

from core.exceptions import InitError


# METHOD DECORATORS


# noinspection PyPep8Naming
#   PyPep8Naming: `classproperty` although a class, follows the same naming
#       convention as the builtin `property` decorator.
class classproperty(property):
    """Decorator that combines behavior of @classmethod and @property.

    Usage:
        class MyClass(object):
            _value = 50
            @classproperty
            READ_ONLY_VALUE(cls):
                return cls._value
        print MyClass.READ_ONLY_VALUE #-> "50"
    """
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


# CLASS DECORATORS


def abstract_class(cls):
    """Mark class as abstract.

    Instructs class's __init__ method to raise `core.exceptions.InitError`
    if instantiated directly.

    Usage:
        @abstract_class
        class MyAbstractClass(object):
            pass
        class MyChildClass(MyAbstractClass):
            pass
        obj = MyChildClass() #-> <MyChildClass object>
        obj = MyAbstractClass() #-> InitError
    """
    orig_init = cls.__init__

    def init(self, *args, **kwargs):
        if self.__class__ == cls:
            raise InitError('Cannot instantiate abstract class.')
        else:
            orig_init(self, *args, **kwargs)

    cls.__init__ = init
    return cls
