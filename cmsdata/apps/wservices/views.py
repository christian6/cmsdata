#!/usr/bin/env python

import json
import time, urllib2
from bs4 import BeautifulSoup

from django.views.generic import View
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from cmsdata.apps.home import forms

from cmsdata.apps.home.models import Materials

class JSONDescription_Materials(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            name = Materials.objects.values('matname').filter(matname__icontains=request.GET.get('description')).distinct('matname').order_by('matname')
            context['mats'] = [{'name': x['matname']} for x in name]
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class JSONMeter_Materials(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            meter = Materials.objects.values('matmet').filter(matname__icontains=request.GET['description']).distinct('matmet').order_by('matmet')
            context['meter'] = [{'meter': x['matmet']} for x in meter]
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class JSONSummary_Materials(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            summ = Materials.objects.filter(matname__icontains=request.GET.get('description'), matmet__icontains=request.GET.get('meter'))[:1]
            context['mats'] = [{'materiales_id': x.materiales_id, 'matname': x.matname, 'matmet': x.matmet, 'unit': x.unit_id} for x in summ]
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class JSONCode_Materials(View):
    def get(self, request, *args, **kwargs):
        context = {}
        try:
            summ = Materials.objects.get(pk__exact=request.GET.get('code'))
            context['mats'] = {'materiales_id': summ.materiales_id, 'matname': summ.matname, 'matmet': summ.matmet, 'unit': summ.unit_id}
            context['status'] = True
        except ObjectDoesNotExist:
            context['status'] = False
        return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class JSONSave_DocumentInDetails(View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            response = HttpResponse()
            response['content_type'] = 'application/json'
            response['mimetype'] = 'application/json'
            context = {}
            try:
                # search materials exists
                form = forms.addDocumentInDetailsForm(request.POST)
                if form.is_valid():
                    form.save()
                    context['status'] = True
                else:
                    context['status'] = False
            except ObjectDoesNotExist:
                context['status'] = False
            response.write(simplejson.dumps(context))
            return response


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