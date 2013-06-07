# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from ..resource import options
import collections
import six
from armet.resources.attributes import Attribute, IntegerAttribute


def _method_to_operation(method):
    if method == 'GET':
        return set(['read'])

    if method == 'PUT':
        return set(['update', 'create', 'delete'])

    if method == 'POST':
        return set(['create'])

    if method == 'PATCH':
        return set(['update', 'create'])

    if method == 'DELETE':
        return set(['destory'])


def _methods_to_operations(methods):
    operations = set()
    for method in operations:
        operations = operations.union(_method_to_operation(method))

    return operations


def _operation_to_method(operation):
    if operation == 'read':
        return set(['GET'])

    if operation == 'update':
        return set(['PUT', 'PATCH'])

    if operation == 'create':
        return set(['PUT', 'PATCH', 'POST'])

    if operation == 'destroy':
        return set(['PUT', 'DELETE'])


def _operations_to_methods(operations):
    methods = set(['HEAD', 'OPTIONS'])
    for operation in operations:
        methods = methods.union(_operation_to_method(operation))

    return methods


class ManagedResourceOptions(options.ResourceOptions):

    def __init__(self, meta, name, data, bases):
        # Initalize base resource options.
        super(ManagedResourceOptions, self).__init__(meta, name, data, bases)

        #! Additional attributes to include in addition to those defined
        #! directly in the resource. This is meant for defining fields
        #! with names that conflict with names used in the resource as
        #! methods. This could be used exclusively; it's a matter of
        #! preference.
        #!
        #! Attributes may also be declared shorthand in a few different
        #! ways. The next few code blocks are identical in function.
        #!
        #! @code
        #! from armet import resources
        #! from armet.resources import attributes
        #! class Resource(resources.Resource):
        #!     name = attributes.Attribute()
        #!     created = attributes.Attribute('created')
        #! @endcode
        #!
        #! @code
        #! from armet import resources
        #! from armet.resources import attributes
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         include = {
        #!             'name': attributes.Attribute()
        #!             'created': attributes.Attribute('created')
        #!         }
        #! @endcode
        #!
        #! @code
        #! from armet import resources
        #! from armet.resources import attributes
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         include = {
        #!             'name': None,
        #!             'created': 'created'
        #!         }
        #! @endcode
        #!
        #! @code
        #! from armet import resources
        #! from armet.resources import attributes
        #! class Resource(resources.Resource):
        #!     class Meta:
        #!         include = ('name',)
        #!     created = attributes.Attribute('created')
        #! @endcode
        self.include = include = meta.get('include', {})
        if not isinstance(include, collections.Mapping):
            # This is a list, tuple, etc. but not a dictionary.
            self.include = {name: Attribute() for name in include}

        else:
            # This is a dictionary; normalize it.
            for key, value in six.iteritems(include):
                if value is None or isinstance(value, six.string_types):
                    include[key] = Attribute(value)

        #! List of allowed operations.
        #! Resource operations are meant to generalize and blur the
        #! differences between "PATCH and PUT", "PUT = create / update",
        #! etc.
        #!
        #! If not provided and http_allowed_methods was provided instead
        #! the methods are appropriately mapped; else, the default
        #! configuration is provided.
        self.allowed_operations = meta.get('allowed_operations')
        if self.allowed_operations is None:
            if meta.get('http_allowed_methods'):
                self.allowed_operations = _methods_to_operations(meta.get(
                    'http_allowed_methods'))

            else:
                self.allowed_operations = (
                    'read',
                    'create',
                    'update',
                    'destroy',
                )

        # Coerce http allowed methods from the
        # allowed operations.
        if meta.get('http_allowed_methods') is None:
            if meta.get('allowed_operations'):
                self.http_allowed_methods = _operations_to_methods(meta.get(
                    'allowed_operations'))

        #! List of allowed HTTP methods against a whole
        #! resource (eg /user); if undeclared or None, will be defaulted
        #! to `http_allowed_methods`.
        self.http_list_allowed_methods = meta.get(
            'http_list_allowed_methods')

        if self.http_list_allowed_methods is None:
            if meta.get('list_allowed_operations'):
                self.http_list_allowed_methods = _operations_to_methods(
                    meta.get('list_allowed_operations'))

            else:
                self.http_list_allowed_methods = self.http_allowed_methods

        #! List of allowed HTTP methods against a single
        #! resource (eg /user/1); if undeclared or None, will be defaulted
        #! to `http_allowed_methods`.
        self.http_detail_allowed_methods = meta.get(
            'http_detail_allowed_methods')

        if self.http_detail_allowed_methods is None:
            if meta.get('detail_allowed_operations'):
                self.http_detail_allowed_methods = _operations_to_methods(
                    meta.get('detail_allowed_operations'))

            else:
                self.http_detail_allowed_methods = self.http_allowed_methods

        #! List of allowed operations against a whole resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.list_allowed_operations = meta.get('list_allowed_operations')

        if self.list_allowed_operations is None:
            if meta.get('http_list_allowed_methods'):
                self.list_allowed_operations = _methods_to_operations(
                    meta.get('http_list_allowed_methods'))

            else:
                self.list_allowed_operations = self.allowed_operations

        #! List of allowed operations against a single resource.
        #! If undeclared or None, will be defaulted to `allowed_operations`.
        self.detail_allowed_operations = meta.get(
            'detail_allowed_operations')

        if self.detail_allowed_operations is None:
            if meta.get('http_detail_allowed_methods'):
                self.detail_allowed_operations = _methods_to_operations(
                    meta.get('http_detail_allowed_methods'))

            else:
                self.detail_allowed_operations = self.allowed_operations

        #! Attribute to use for the slug or url segment
        #! that identifies the resource. The slug attribute is
        #! a special attribute; there are a couple of requirements.
        #! One is that it must be a unique reference. A /url/slug must
        #! return at most one item. Second is that as it is a special
        #! attribute that is not part of the body there is not
        #! a `prepare_slug` method; however, there is a `slug_prepare` method
        #! that accomplishes the same purpose. This is to allow for a
        #! normal attribute that is named slug.
        self.slug = meta.get('slug')
        if self.slug is None:
            # The slug defaults to `id`; which on most model engines
            # is the primary key. This is as good as a default as any I
            # suppose.
            self.slug = IntegerAttribute('id')
