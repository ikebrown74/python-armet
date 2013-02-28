# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.conf import urls
from django.views.decorators import csrf
from armet import utils
from armet.resources import base, meta, options


class ResourceOptions(options.ResourceOptions):
    def __init__(self, options, name, bases):
        super(ResourceOptions, self).__init__(options, name, bases)
        #! URL namespace to define the url configuration inside.
        self.url_name = options.get('url_name')
        if not self.url_name:
            self.url_name = 'api_view'


class ResourceBase(meta.ResourceBase):
    options = ResourceOptions


class Resource(six.with_metaclass(ResourceBase, base.Resource)):
    """Specializes the RESTFul resource protocol for django.

    @note
        This is not what you derive from to create resources. Import
        Resource from `armet.resources` and derive from that.
    """

    @classmethod
    @csrf.csrf_exempt
    def redirect(cls, request, *args, **kwargs):
        request.path = super(Resource, cls).redirect(request.path)
        return HttpResponsePermanentRedirect(request.get_full_path())

    @classmethod
    @csrf.csrf_exempt
    def view(cls, request, *args, **kwargs):
        # Initiate the base view request cycle.
        # TODO: response will likely be a tuple containing headers, etc.
        response = super(Resource, cls).view(kwargs.get('path'))

        # Construct an HTTP response and return it.
        return HttpResponse(response)

    @classmethod
    def url(cls, url, method):
        """Builds the URL pattern for an single URL of this resource."""
        return urls.url(url.format(cls.meta.name), method,
            name=cls.meta.url_name,
            kwargs={'resource': cls.meta.name})

    @utils.classproperty
    def urls(cls):
        """Builds the URL configuration for this resource."""
        view = cls.view if cls.meta.trailing_slash else cls.redirect
        redirect = cls.redirect if cls.meta.trailing_slash else cls.view
        return urls.patterns('',
            cls.url(r'^{}(?P<path>.*)/', view),
            cls.url(r'^{}(?P<path>.*)', redirect),
            cls.url(r'^{}/', view),
            cls.url(r'^{}', redirect),
        )
