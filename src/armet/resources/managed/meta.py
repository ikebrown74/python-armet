# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from armet.resources.attributes import Attribute
from ..resource.meta import ResourceBase
from . import options


class ManagedResourceBase(ResourceBase):

    options = options.ManagedResourceOptions

    def __new__(cls, name, bases, attrs):
        # Construct the class object.
        self = super(ManagedResourceBase, cls).__new__(cls, name, bases, attrs)

        if not cls._is_resource(name, bases):
            # This is not an actual resource.
            return self

        # Gather declared attributes from ourself and base classes.
        # TODO: We'll likely need a hook here for ORMs
        self.attributes = attributes = {}
        for base in bases:
            if hasattr(base, 'attributes'):
                attributes.update(**base.attributes)

        for index, attribute in six.iteritems(attrs):
            if isinstance(attribute, Attribute):
                attributes[index] = attribute

        # Append include directives here
        attributes.update(**self.meta.include)

        # Cache access to the attribute preparation cycle.
        self.preparers = preparers = {}
        for key in attributes:
            prepare = getattr(self, 'prepare_{}'.format(key), None)
            if not prepare:
                prepare = lambda s, o, v: v
            preparers[key] = prepare

        # Return the constructed class object.
        return self