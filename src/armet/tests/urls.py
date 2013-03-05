# -*- coding: utf-8 -*-
""" Defines an empty root URL configuration.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.conf.urls import patterns, url, include
from . import api


urlpatterns = patterns('',
    url('^api/', include(api.Poll.urls)),
    url('^', include(api.Choice.urls)),
    url('^', include(api.BoothSomethignElseBlahBlah.urls)),
    url('^', include(api.Cushion.urls))
)
