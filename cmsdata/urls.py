# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
# from django.conf import settings
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cmsdata.views.home', name='home'),
    # url(r'^cmsdata/', include('cmsdata.foo.urls')),
    url(r'', include('cmsdata.apps.home.urls')),
    url(r'^restful/', include('cmsdata.apps.wservices.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$','django.views.static.serve', {'document_root':settings.MEDIA_ROOT}),
)