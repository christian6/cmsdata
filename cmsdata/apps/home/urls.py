#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('',
    url(r'^accounts/login/$', ViewLogin.as_view(), name='view_login'),
    url(r'^accounts/logout/$', ViewLogout.as_view(), name='view_logout'),
    url(r'^$', ViewHome.as_view(), name='view_home'),

    url(r'^list/document/entry/', ViewListDocumentEntry.as_view(), name='view_list_entry'),
    url(r'^list/document/output/', ViewListDocumentOutput.as_view(), name='view_list_output'),
    url(r'^add/document/In/$', ViewDocumentIn.as_view(), name='view_add_docin'),
    url(r'^add/document/output/$', ViewDocumentOut.as_view(), name='view_add_docout'),
    url(r'^add/materials/$', ViewMaterials.as_view(), name='view_add_mat'),
    url(r'^add/suppliers/$', ViewSupplier.as_view(), name='view_add_sup'),
    url(r'^consult/materials/$', ViewSearchMaterialsPrice.as_view(), name='view_consult'),
    url(r'^contruct/inventory/$', ViewConstructInventory.as_view(), name='view_construct'),
)