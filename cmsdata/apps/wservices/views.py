#!/usr/bin/env python

import time, urllib2
from bs4 import BeautifulSoup

from django.views.generic import View
from django.http import HttpResponse
from django.utils import simplejson

class JsonSunatData(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            url = 'http://www.sunat.gob.pe/w/wapS01Alias?ruc=%s'%(request.GET.get('ruc'))
            data = parseSunat(url)
            if data != 'Nothing':
                soup = BeautifulSoup(data)
                for x in soup.find_all('small'):
                    tag = BeautifulSoup(x.__str__())
                    #print tag
                    conditional = tag.body.small.contents[0].string
                    if conditional.endswith('Ruc. '):
                        res = tag.body.small.contents[1]
                        res = res.split('-',1)
                        context['ruc'] = res[0].strip()
                        context['reason'] = res[1].strip()
                    if conditional.startswith('Direcci'):
                        context['address'] = tag.body.small.contents[2].string
                    if conditional.startswith('Tipo.'):
                        context['type'] = tag.body.small.contents[2]
                    if conditional.startswith('Tel'):
                        context['phone'] = tag.body.small.contents[2]
                    if conditional.startswith('DNI'):
                        context['dni'] = tag.body.small.contents[1].string[3:]
                    context['status'] = True
            else:
                context['status'] = False
        except Exception, e:
            contet['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype="application/json")

def parseSunat(url):
    try:
        req = urllib2.Request(url)
        return urllib2.urlopen(req).read()
    except Exception:
        return "Nothing"