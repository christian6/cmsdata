#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('',
    url(r'^search/sunat/ruc/$', JsonSunatData.as_view()),
    # Search Concurrent
    url(r'^materials/name/$', JSONDescription_Materials.as_view()),
    url(r'^materials/meter/$', JSONMeter_Materials.as_view()),
    url(r'^materials/summary/$', JSONSummary_Materials.as_view()),
    url(r'^materials/code/$', JSONCode_Materials.as_view()),
    # Documents Entry Details
    url(r'^document/in/details/save/$', JSONSave_DocumentInDetails.as_view()),
)