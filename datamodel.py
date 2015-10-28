"""Data Model/Controller classes.

Allows creation of controller classes with integrated data models with
one-way data-binding.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Collection -- Used for type definition in the `DataModel` rule-set
        to track deep data members such as `dict` and `list`.
    :class DataModel -- The read-only data-model passed to controller
        event-listeners. This model contains a read-only, storage-ready
        representation of the Pythonic data on the controller. This
        should not be instantiated from outside the
        `DataModelController.__init__` method.
    :class DataModelController -- Main controller class. New controllers
        inherit from this.
"""

from core.decorators import classproperty, abstract_class


@abstract_class
class Collection(object):
    """Class for specifying Collection type in `DataModel`.

    While the Collection class can be used for type comparison, it is not
    meant to be instantiated. Instead use the `Collection.List` or
    `Collection.Dict` sub-classes.

    Init Params:
        subtype - Optional type restriction for collection elements.

    Usage:
        Collection.List(<type|None>) -- Generates a list collection with
            a rule restricting the items to the given type.
        Collection.Dict(<type|None>) -- Generates a list collection with
            a rule restricting the values to the given type.
        Collection.List -- Same as Collection.List(None): Does not
            restrict item type.
        Collection.Dict -- Same as Collection.Dict(None): Does not
            restrict value type.
    """

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    def List(cls):
        return CollectionList

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    def Dict(cls):
        return CollectionDict

    # noinspection PyMethodParameters
    @classproperty
    def subtype(cls):
        return None

    def __init__(self, subtype=None):
        if subtype is None:
            subtype = self.__class__.subtype
        self._subtype = subtype

    @property
    def subtype(self):
        return self._subtype


class DataModel(object):
    """Read-only representation of data.

    Contains read-only properties for each data-field defined by containing
    controller class.

    Note:
        Should only be initialized from within `DataModelController` class.

    Init Params:
        rules - A dictionary of `DataModel` keys mapped to tuples containing
            the attribute name(s) to bind, the value type, and an optional
            mapping function, respectively.

    Public Methods:
        update_key - Update model for given key.
        update_all - Update model for all keys.
        update_from_binding - Update all model keys associated with binding.
    """

    class Rule(object):
        """Holds data for individual binding rule.

        Properties:
            :type self.type: type | Collection | None -- Used for enforcement
                of strict typing within `DataModel`.
            :type self.binding: str | None -- The name of the attribute on the
                controller to which the `DataModel` key is bound. If None, key
                is bound to controller instance.
            :type self.operation: callable (mixed) -> mixed -- Function rule for
                converting data from controller attribute into form accepted by
                `DataModel` key.
        """
        @classmethod
        def default_operation(cls, scope):
            """Mapping function to use for key value if none defined.

            Current default is identity function.
            """
            return scope

        def __init__(self, binding, datatype, operation):
            """DataModel.Rule init

            :param binding: str | list | None -- Name of bound Controller
                attribute(s). If None value will be bound to root controller
                instance.
            :param datatype: type | Collection | None -- Type rule for value.
                If None value will have no type restriction.
            :param operation: None | callable (mixed) -> mixed -- Optional
                mapping function that takes the bound attribute and produces
                the value to be stored in the `DataModel`.
            """
            self._binding, self._type = binding, datatype
            if operation is None:
                operation = self.__class__.default_operation
            self._operation = operation

        @property
        def type(self): return self._type

        @property
        def binding(self): return self._binding

        @property
        def operation(self): return self._operation

    def __init__(self, rules):
        """DataModel init

        :param rules: dict -- The rule-set for each DataModel key.

        :raises NameError if rules contain data-key sharing the name of an
            existing member.
        """
        self.__locked = False
        self.__data = {}
        self.__rules = {}
        for key, val in rules.iteritems():
            if hasattr(self, key):
                raise NameError('Invalid DataModel key name: ' + key)
            self.__rules[key] = DataModel.Rule(*val)
        self.__locked = True

    def update_key(self, ref, key, instruction=None):
        """Update the value for the given key.

        :param ref: DataModelController -- The controller instance.
        :param key: str -- The data field name within the model.
        :param instruction: dict | None -- Optional instruction set for precise
            updates of a Collection type. If None, the entire collection is
            re-assigned / re-generated.
            Expected Keys For Collection.List:
                :key action: str -- The instruction type. Always required.
                    Possible values consist of 'remove', 'append' and 'insert'.
                :key index: int -- The index of item affected by the action.
                    Required with actions 'remove' and 'insert'.
            Expected Keys For Collection.Dict:
                :key action: str -- The instruction type. Always required.
                    Possible values consist of 'remove', and 'add'.
                :key key: str -- The key of the value affected by the action.
                    Always required.

        :raises AttributeError if provided key does not exist.
        :raises ValueError if provided instruction has an invalid action.
        :raises TypeError if updated value does not conform to the defined
            type rules.
        """
        if key in self.__rules:
            rule = self.__rules[key]
            value = ref
            operation = rule.operation
            if rule.binding:
                value = ref.__dict__[rule.binding]
            if rule.type:
                if isinstance(rule.type, Collection) or \
                        issubclass(rule.type, Collection):
                    subtype = rule.type.subtype
                    if isinstance(rule.type, Collection.List) or \
                            issubclass(rule.type, Collection.List):
                        if instruction:
                            if instruction['action'] == 'remove':
                                item = self.__data[key][instruction['index']]
                                self.__data[key].remove(item)
                            elif instruction['action'] == 'append':
                                item = operation(value[len(value)-1])
                                if subtype and not isinstance(item, subtype):
                                    raise TypeError('Item of invalid type '
                                                    'in collection: ' + key)
                                self.__data[key].append(item)
                            elif instruction['action'] == 'insert':
                                item = operation(value[instruction['index']])
                                if subtype and not isinstance(item, subtype):
                                    raise TypeError('Item of invalid type '
                                                    'in collection: ' + key)
                                self.__data[key].insert(instruction['index'],
                                                       item)
                            else:
                                raise ValueError(
                                    'collection.list cannot handle instruction'
                                    ' type: ' + instruction['action'])
                        else:
                            if not isinstance(value, list):
                                raise TypeError('Datamodel expected value with'
                                                ' type `list` for collection'
                                                ': ' + key)
                            for x in value:
                                y = operation(x)
                                if subtype and not isinstance(y, subtype):
                                    raise TypeError('Item of invalid type '
                                                    'in collection: ' + key)
                            self.__data[key] = [operation(x) for x in value]

                    elif isinstance(rule.type, Collection.Dict) or \
                            issubclass(rule.type, Collection.Dict):
                        if instruction:
                            if instruction['action'] == 'remove':
                                del self.__data[key][instruction['key']]
                            elif instruction['action'] == 'add':
                                item = operation(value[instruction['key']])
                                if subtype and not isinstance(item, subtype):
                                    raise TypeError('Item of invalid type '
                                                    'in collection: ' + key)
                                self.__data[key][instruction['key']] = item
                            else:
                                raise ValueError(
                                    'collection.dict cannot handle instruction'
                                    ' type: ' + instruction['action'])
                        else:
                            if not isinstance(value, dict):
                                raise TypeError('Datamodel expected value with'
                                                ' type `dict` for collection'
                                                ': ' + key)
                            self.__data[key] = {}
                            for k, v in value.iteritems():
                                y = operation(v)
                                if subtype and not isinstance(y, subtype):
                                    raise TypeError('Item of invalid type '
                                                    'in collection: ' + key)
                                self.__data[k] = y
                else:
                    if not isinstance(value, rule.type):
                        raise TypeError('Datamodel expected value with type '
                                        '`' + rule.type.__name__ + '` for key: ' + key)
                    self.__data[key] = operation(value)
            else:
                self.__data[key] = operation(value)
        else:
            raise AttributeError

    def update_all(self, ref):
        """Update entire model.

        Calls `update_key` for every key in the rule set.

        :param ref: DataModelController -- The controller instance.

        :raises TypeError if updated value does not conform to the defined
            type rules.
        """
        for key, val in self.__rules.iteritems():
            self.update_key(ref, key)

    def get_bindings_for_key(self, key):
        return self.__rules[key].binding

    def update_from_binding(self, ref, bound_attr_name=None):
        """Update model keys associated with given controller attribute.

        :param ref: DataModelController -- The controller instance.
        :param bound_attr_name: str | list | None -- If None, the entire model
            is updated.
        :return set -- The set of keys that are associated with the attribute
            name(s) given.

        :raises TypeError if updated value does not conform to the defined
            type rules.
        """
        keys = set()
        if not bound_attr_name:
            self.update_all(ref)
            keys = set(self.__rules.keys())
        elif isinstance(bound_attr_name, (list, set, tuple)):
            for key, val in self.__rules.iteritems():
                if (not val.binding or val.binding in bound_attr_name or
                    (isinstance(val.binding, (list, set, tuple)) and
                     bool([x for x in val.binding if x in bound_attr_name]))):
                    self.update_key(ref, key, None)
                    keys.add(key)
        else:
            for key, val in self.__rules.iteritems():
                if (not val.binding or val.binding in bound_attr_name or
                    (isinstance(val.binding, (list, set, tuple)) and
                     bound_attr_name in val.binding)):
                    self.update_key(ref, key, None)
                    keys.add(key)
        return keys

    def __getattr__(self, key):
        if key in self.__data:
            return self.__data[key]
        else:
            raise AttributeError

    def __setattr__(self, key, value):
        if hasattr(self, '_locked') and self.__locked:
            raise ValueError('Cannot change values from read-only proxy.')
        else:
            super(DataModel, self).__setattr__(key, value)

    def __str__(self):
        return str(self.__data)

    def __repr__(self):
        return str(self)


@abstract_class
class DataModelController(object):
    """Controller for `DataModel`.

    Abstract class to be inherited by all Controllers. Contains private and
    public methods for handling data modeling and binding.

    Init Params:
        rules - A dictionary of `DataModel` keys mapped to tuples containing
            the attribute name to be bound to, the value type, and an optional
            mapping function, respectively.

    Private Methods -- To be used inside children classes:
        _update_model -- Update all `DataModel` keys bound to the give attribute
            name(s).
        _update_model_collection -- Send update instruction to the `DataModel`
            for a specific Collection. This streamlines the update within the
            model, so that the entire collection does not need to be
            re-assigned or re-generated.
        _call_listener -- Fire event listeners for the given bound attribute
            name(s).

    Public Methods:
        on_change
        off_change

    Properties:
        :type self.model: DataModel -- The `DataModel` owned by the controller.

    Usage:
        class MyController(DataModelController):
            def __init__(self):
                super(MyController, self).__init__({<Field Name>: (
                        <binding name|[<binding names>]>, <type>, <lambda operation>)})
        ctrl = MyController()
        ctrl.on_change(<binding name>, <func DataModel str dict|None (*args)>, *args)

    Example:
        class PhoneRecord(DataModelController):
            # Phone record with object attributes of `name`, `number`, `id`;
            #   and a datamodel representation with keys of `firstname`,
            #   `lastname`, `number`, `id`; all bound to the instance attrs.
            ID = 1
            def __init__(self, name, number):
                self.name, self.number, self.id = name, number, PhoneRecord.ID
                PhoneRecord.ID += 1
                rules = {
                    'firstname': ('name', str,
                                  lambda scope: scope[:scope.index(' ')]),
                    'lastname': ('name', str,
                                 lambda scope: scope[scope.index(' ')+1:]),
                    'number': ('number', str, None),
                    'id': ('id', int, None)}
                super(PhoneRecord, self).__init__(rules)
        class PhoneBook(DataModelController):
            # Phone book with object attributes of `records`, `last_id`;
            #   and a datamodel representation with keys of `records`,
            #   `last_id`; again, bound to the instance attributes.
            def __init__(self):
                self.records = []
                self.last_id = 0
                rules = {
                    'records': ('records', Collection.List(DataModel),
                                lambda scope: scope.model),
                    # The datamodel field of `records` contains the ruleset
                    #   which defines the bound instance attribute name of
                    #   'records', which is a Collection.List of DataModels,
                    #   and each element of PhoneBook.records is mapped by
                    #   taking only the `model` attribute to satisfy the type
                    #   restriction.
                    'last_id': ('last_id', int, None)}
                super(PhoneBook, self).__init__(rules)
            def record_changed(self, model, key, instruction, msg):
                print model.firstname + msg
            def add_record(self, name, number):
                record = PhoneRecord(name, number)
                record.on_change('*', self.record_changed, [' has been updated!'])
                self.last_id = record.id
                self.records.append(record)
                self._update_model_collection('records', 'records', {'action': 'append'})
        my_book = PhoneBook()
        print my_book.model #-> "{'records': [], 'last_id': 0}"
        my_book.add_record('Gene Belcher', '555-1234')
        my_book.add_record('Louise Belcher', '555-2345')
        print my_book.model #-> "{'records': [
        #   {'lastname': 'Belcher', 'number': '555-1234', 'firstname': 'Gene', 'id': 1},
        #   {'lastname': 'Belcher', 'number': '555-2345', 'firstname': 'Louise', 'id': 2}],
        #   'last_id': 2}"
        print my_book.model.records[0].model.firstname #-> "Gene"
        gene = my_book.records[0]
        gene.name = 'Gene The Magic Man Belcher' #-> "Gene has been updated!"
        print my_book.model #-> "{'records': [
        #   {'lastname': 'The Magic Man Belcher', 'number': '555-1234', 'firstname': 'Gene', 'id': 1},
        #   {'lastname': 'Belcher', 'number': '555-2345', 'firstname': 'Louise', 'id': 2}],
        #   'last_id': 2}"
        gene.model.lastname = 'Belcher' #-> ValueError (Cannot change values from read-only proxy.)
    """

    @property
    def model(self):
        return self.__model

    def __init__(self, rules):
        """DataModelController init

        :param rules: dict -- The DataModel keys and associated rules.

        :raises NameError if rules contain data-key sharing the name of an
            existing `DataModel` member.
        """
        self.__listeners = {}
        self.__bindings = []
        for k, v in rules.iteritems():
            if v[0]:
                self.__bindings.append(v[0])
        self.__keys = [k for k in rules.iteritems()]
        self.__model = DataModel(rules)
        self.__model.update_all(self)

    def get_prop_for_key(self, key):
        if key not in self.__keys:
            raise ValueError("Key does not exist in DataModel.")
        attr_name = self.model.get_bindings_for_key(key)
        # If more than one binding for key, this only gets the first property
        #   binding in the list. This could cause potential logic problems
        #   in the future and should be dealt with eventually.
        if isinstance(attr_name, (list, set, tuple)):
            attr_name = attr_name[0]
        return getattr(self, attr_name)

    def on_change(self, key, func, args=None):
        """Add listener for changed DataModel value(s).

        :param key: str | list -- If '*' all keys will be bound. Allows
            scoped listeners to be added using dot notation.
            Example:
                ctrl.on_change('sub_ctrl.sub_sub_ctrl.key
        :param func: callable (model, key, instruction, [args,...]) -- The
            event handler.
        :param args: list | None -- Optional additional args to pass to the
            handler function.
        """
        if key == '*':
            key = self.__keys
        if isinstance(key, (set, list, tuple)):
            for k in key:
                self.on_change(k, func, args)
        elif isinstance(key, str) and '.' in key:
            keys = key.split('.')
            final_key = keys.pop()
            scope = self
            for k in keys:
                scopes = None
                if isinstance(scope, (list, set, tuple)):
                    scopes = scope
                    scope = scopes[0]
                if not scope.has_data_key(k):
                    raise ValueError("Bad param supplied. No `" + k +
                                     "` property.")
                if scopes:
                    scope = [obj.get_prop_for_key(k) for obj in scopes]
                else:
                    scope = scope.get_prop_for_key(k)
            if isinstance(scope, list):
                for s in scope:
                    s.on_change(final_key, func, args)
            else:
                scope.on_change(final_key, func, args)
        elif key in self.__keys:
            if key not in self.__listeners:
                self.__listeners[key] = []
            self.__listeners[key].append((func, args))
        else:
            raise ValueError("Key `' + key + '` does not exist in DataModel.")

    def off_change(self, key):
        """Remove listeners for given DataModel key(s).

        :param key: str | list -- If '*' all keys will be unbound from their
            respective listeners.
        """
        if key == '*':
            key = self.__bindings
        if isinstance(key, (set, list, tuple)):
            for k in key:
                self.off_change(k)
        else:
            del self.__listeners[key]

    def _update_model_collection(self, key, instruction):
        """Precise update of a `Collection`.

        :param key: str | list -- The key(s) of the `DataModel` where the
            `Collection` is stored.
        :param instruction: dict -- Instruction set. See docs for
            `DataModel.update_key`.
        """
        if isinstance(key, (list, tuple, set)):
            for k in key:
                self.__model.update_key(self, k, instruction)
        else:
            self.__model.update_key(self, key, instruction)
        self._call_listener(key, instruction)

    def _update_model(self, bindings=None):
        """Update `DataModel` for given bound attribute name(s).

        :param bindings: str | list | None -- if None update entire model.
        """
        if bindings is None:
            bindings = self.__bindings
        keys = self.__model.update_from_binding(self, bindings)
        self._call_listener(keys)

    def _call_listener(self, keys, instruction=None, kwargs=None):
        """ Call listener

        :param keys: str | set | list -- The key(s) that have been updated.
        :param instruction: dict - The optional instruction if the update was
            a precise collection update.
        """
        if not instruction:
            instruction = kwargs
        elif kwargs is not None:
            instruction.update(kwargs)
        if isinstance(keys, (list, set, tuple)):
            for key in keys:
                self._call_listener(key, instruction, kwargs)
        elif keys in self.__listeners:
            for listener in self.__listeners[keys]:
                if callable(listener[0]):
                    listener[0](self.model, keys, instruction, *listener[1])

    def __setattr__(self, key, value):
        super(DataModelController, self).__setattr__(key, value)
        try:
            if self.__bindings and key in self.__bindings:
                self._update_model(key)
        except NameError:
            pass


class CollectionList(Collection):
    """Private class used for aliasing as `Collection.List`."""
    pass


class CollectionDict(Collection):
    """Private class used for aliasing as `Collection.Dict`."""
    pass
