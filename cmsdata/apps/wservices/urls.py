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
    url(r'^document/in/details/list/$', JSONList_DocumentInDetails.as_view()),
    url(r'^document/in/details/edit/$', JSONEdit_DocumentEntryDetails.as_view()),
    url(r'^document/in/details/delete/$', JSONDelete_DocumentEntryDetails.as_view()),
    url(r'^document/in/finish/$', JSONFinish_DocumentEntry.as_view()),
    # Documents Output Details
    url(r'^document/out/details/save/$', JSONSave_DocumentOutputDetails.as_view()),
    url(r'^document/out/details/list/$', JSONList_DocumentOutputDetails.as_view()),
    url(r'^document/out/details/edit/$', JSONEdit_DocumentOutputDetails.as_view()),
    url(r'^document/out/details/delete/$', JSONDelete_DocumentOutputDetails.as_view()),
    url(r'^document/out/finish/$', JSONFinish_DocumentOutput.as_view()),
    # consult
    url(r'^search/price/code/$', JSONSearchCode_Price.as_view()),
    url(r'^search/price/description/$', JSONSEarchDescription_Price.as_view()),
)