#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('',
    url(r'^search/sunat/ruc/$', JsonSunatData.as_view()),
)