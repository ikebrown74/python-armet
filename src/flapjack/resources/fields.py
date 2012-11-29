# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from .. import utils


class Field(object):

    def __init__(self, **kwargs):
        #! Whether this field can be modified or not.
        self.editable = kwargs.get('editable', False)

        #! Whether this field is a collection or not.
        self.collection = kwargs.get('collection', False)

        #! Whether this field may be filtered or not.
        self.filterable = kwargs.get('filterable', False)

        #! Visibility of the field.
        self.visible = kwargs.get('visible', False)

        #! Whether this fields is bound to a model or not.
        self.model = kwargs.get('model', False)

        #! Accessor functions that will get the value of the field
        #! from a obj.
        self.accessors = kwargs.get('accessors', [])

        #! Preparation function that is linked to the class object of the
        #! instantiating resource.
        self.prepare = kwargs.get('prepare')

        #! Path of the field; storing for interesting purposes.
        self.path = kwargs.get('path')

        #! Stored segments that correspond to lazily evaluated accessors.
        self._segments = self.path.split('__')

        #! Stored relation reference.
        self._relation = kwargs.get('relation')

    @property
    def relation(self):
        if self._relation is not None:
            if not isinstance(self._relation[0], type):
                # Resolve resource class object
                self._relation[0] = utils.load(self._relation[0])

            # Resource class object is already resolved; return it.
            return self._relation

        # No relation; nothing to do.
        return None

    def accessor(self, value):
        for accessor in self.accessors:
            # Iterate and access the entire field path
            value = accessor(value)

        if value is not None and self._segments:
            depth = 0
            for segment in self._segments:
                # If additional accessors are needed; build them now
                accessor = self._build_accessor(value.__class__, segment)

                # Append the accessor
                self.accessors.append(accessor)

                # Use the accessor
                value = accessor(value)

                # Increment depth
                depth += 1

            # Remove segments used
            self._segments = self._segments[depth:]

        # Return what we've accessed
        return value

    def clean(self, value):
        """Cleans the value for consumption by the form clean cycle."""
        # Base field class just passes the value through.
        return value

    def _build_accessor(self, cls, name):
        obj = getattr(cls, name, None)
        if obj is not None:
            if hasattr(obj, '__get__'):
                # A readable descriptor at the very least
                return lambda o, x=obj.__get__: x(o)

        if hasattr(cls, '__getitem__'):
            # Some kind of mapping; use dictionary access.
            return lambda o, n=name: o[name]

        # No alternative; attempt direct attribute access using the instance
        # dictionary.
        return lambda o, n=name: o.__dict__[n]


class ModelField(object):

    def _build_accessor(self, cls, name):
        obj = getattr(cls, name, None)
        if obj is not None:
            if hasattr(obj, 'related_manager_cls'):
                # Relation where it is a {1,*}-*
                return lambda o, x=obj.__get__: x(o).all()

        # No alternative; let the base take it.
        return super(ModelField, self)._build_accessor(cls, name)


class BooleanField(Field):

    #! Values accepted for `True`.
    TRUE = (
        'true',
        't',
        'yes',
        'y',
        'on'
        '1'
    )

    #! Values accepted for `False`.
    FALSE = (
        'false',
        'f',
        'no',
        'n',
        'off',
        '0'
    )

    def clean(self, value):
        if value.strip().lower() in self.TRUE:
            # Some sort of truthy value.
            return True

        if value.strip().lower() in self.FALSE:
            # Some sort of falsy value.
            return False

        # Neither true or false matches; return what we were given.
        return value


class DateField(Field):
    pass


class TimeField(Field):
    pass


class DateTimeField(Field):
    pass


class FileField(Field):
    pass