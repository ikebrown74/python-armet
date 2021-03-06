# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import armet
from armet import utils
from . import options


#! Map of connector class objects in their connector modules.
CONNECTORS = {
    'http': {
        'resource': ('{}.resources', 'Resource',),
        'options': ('{}.resources', 'ResourceOptions',)
    },
    'model': {
        'resource': ('{}.resources', 'ModelResource',),
        'options': ('{}.resources', 'ModelResourceOptions',)
    }
}


class ResourceBase(type):

    #! Options class to use to expand options.
    options = options.ResourceOptions

    #! Connectors to instantiate and mixin to the inheritance.
    connectors = ['http']

    def __getattribute__(self, name):
        if name == 'connectors' or name.startswith('__'):
            # Return immediately.
            return super(ResourceBase, self).__getattribute__(name)

        # Attempt to get the attribute from a connector.
        connectors = self.__dict__.get('connectors')
        if connectors and isinstance(connectors[0], type):
            for connector in self.connectors:
                attr = connector.__dict__.get(name)
                if attr is not None:
                    # Found attribute.
                    if hasattr(attr, '__get__'):
                        # This has a descriptor; wrap it to use the
                        # current cls.
                        return attr.__get__(None, self)
                        # return lambda *a, **kw: attr.__get__(self, *a, **kw)

                    # Return a normal attribute.
                    return attr

        # Found nothing; continue as normal.
        return super(ResourceBase, self).__getattribute__(name)

    @classmethod
    def _is_resource(cls, name, bases):
        if name == 'NewBase':
            # This is a six contrivance; not a real class.
            return False

        if name.startswith('armet.connector:'):
            # This is special mixed connector class; not something
            # to run the metaclass over.
            return False

        for base in bases:
            if base.__name__ == 'NewBase':
                # This is a six contrivance; move along.
                continue

            if isinstance(base, cls):
                # This is some sort of derived resource; good.
                return True

        # This is not derived at all from Resource (eg. is base).
        return False

    @classmethod
    def _gather_metadata(cls, metadata, bases):
        for base in bases:
            if isinstance(base, cls) and hasattr(base, 'Meta'):
                # Append metadata.
                metadata.append(getattr(base, 'Meta'))

                # Recurse.
                cls._gather_metadata(metadata, base.__bases__)

    def __new__(cls, name, bases, attrs):
        if not cls._is_resource(name, bases):
            # This is not an actual resource.
            return super(ResourceBase, cls).__new__(cls, name, bases, attrs)

        # Gather the attributes of all options classes.
        # Start with the base configuration.
        metadata = armet.use().copy()
        values = lambda x: {n: getattr(x, n) for n in dir(x)}

        # Expand the options class with the gathered metadata.
        base_meta = []
        cls._gather_metadata(base_meta, bases)

        # Apply the configuration from each class in the chain.
        for meta in base_meta:
            metadata.update(**values(meta))

        cur_meta = {}
        if attrs.get('Meta'):
            # Apply the configuration from the current class.
            cur_meta = values(attrs['Meta'])
            metadata.update(**cur_meta)

        # Gather and construct the options object.
        meta = attrs['meta'] = cls.options(metadata, name, cur_meta, base_meta)

        # Construct the class object.
        self = super(ResourceBase, cls).__new__(cls, name, bases, attrs)

        # Generate a serializer map that maps media ranges to serializer
        # names.
        self._serializer_map = smap = {}
        for key in self.meta.allowed_serializers:
            serializer = self.meta.serializers[key]
            for media_type in serializer.media_types:
                smap[media_type] = key

        # Generate a deserializer map that maps media ranges to deserializer
        # names.
        self._deserializer_map = dmap = {}
        for key in self.meta.allowed_deserializers:
            deserializer = self.meta.deserializers[key]
            for media_type in deserializer.media_types:
                dmap[media_type] = key

        # Filter the available connectors according to the
        # metaclass restriction set.
        for key in list(meta.connectors.keys()):
            if key not in cls.connectors:
                del meta.connectors[key]

        # Iterate through the available connectors.
        iterator = six.iteritems(meta.connectors)
        self.connectors = connectors = []
        cmap = CONNECTORS
        for key, ref in iterator:
            options = utils.import_module(cmap[key]['options'][0].format(ref))
            if options:
                options = getattr(options, cmap[key]['options'][1], None)
                if options:
                    # Available options to parse for this connector;
                    # instantiate the options class and apply all
                    # available options.
                    options_instance = options(metadata, name, base_meta)
                    meta.__dict__.update(**options_instance.__dict__)

            module = utils.import_module(cmap[key]['resource'][0].format(ref))
            if module:
                klass = getattr(module, cmap[key]['resource'][1], None)
                if klass:
                    # Found a connector class for this connector
                    connectors.append(klass)

        # Return the constructed instance.
        return self
