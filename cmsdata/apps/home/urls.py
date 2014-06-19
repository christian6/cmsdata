#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('',
    url(r'^accounts/login/$', ViewLogin.as_view(), name='view_login'),
    url(r'^accounts/logout/$', ViewLogout.as_view(), name='view_logout'),
    url(r'^$', ViewHome.as_view(), name='view_home'),
)