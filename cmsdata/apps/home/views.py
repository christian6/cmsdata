#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_list_or_404
from django.views.generic.base import TemplateView, View
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.template import RequestContext
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from .forms import *
from .models import *

### Class Views Generic Base
  
class ViewLogin(TemplateView):
    template_name = "home/login.html"

    def get_context_data(self, **kwargs):
        context = super(ViewLogin, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            return HttpResponseRedirect('/')

        context['form'] = logininForm()
        return context

    def post(self, request, *args, **kwargs):
        try:
            form = logininForm(request.POST)
            if form.is_valid():
                print "form validate"
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                usuario = authenticate(username=username,password=password)
                if usuario is not None and usuario.is_active:
                    login(request,usuario)
                    return HttpResponseRedirect('/')
                else:
                    message = "Usuario o Password incorrecto"
            else:
                message = "Usuario o Password no son validos!"
                context = { 'form': logininForm(), 'msg': message }
            return render_to_response('home/login.html', context, context_instance=RequestContext(request))
        except Exception, e:
            raise Http404("Method no proccess")

class ViewLogout(TemplateView):
    template_name = "home/logout.html"

    def get_context_data(self, **kwargs):
        context = super(ViewLogout, self).get_context_data(**kwargs)
        logout(self.request)
        return HttpResponseRedirect('/')

class ViewHome(TemplateView):
    template_name = "home/home.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ViewHome, self).dispatch(request, *args, **kwargs)

class ViewListDocumentEntry(TemplateView):
    template_name = "home/listdocentry.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = super(ViewListDocumentEntry, self).get_context_data(**kwargs)
        if request.GET.get('search') != '':
            if request.GET.get('search') == 'status':
                model = DocumentIn.objects.filter(flag=True, status=request.GET.get('status'))
            else:
                if request.GET.get('dend') == '' :
                    model = DocumentIn.objects.filter(flag=True, transfer=request.GET.get('dstart'))
                else:
                    model = DocumentIn.objects.filter(flag=True, transfer__range=(request.GET.get('dstart'), request.GET.get('dend')) )
        else:
            model = DocumentIn.objects.filter(flag=True, status='PE')
        paginator = Paginator(model, 10)
        page = request.GET.get('page')
        try:
            documents = paginator.page(page)
        except PageNotAnInteger:
            documents = paginator.page(1)
        except EmptyPage:
            documents = paginator.page(paginator.num_pages)
        context['documents'] = documents
        return render_to_response(self.template_name, context, context_instance=RequestContext(request))

class ViewDocumentIn(TemplateView):
    template_name = "home/documentin.html"

class ViewDocumentOut(TemplateView):
    template_name = "home/documentin.html"

class ViewMaterials(TemplateView):
    template_name = "home/documentin.html"

class ViewSupplier(TemplateView):
    template_name = "home/documentin.html"


"""
import time, urllib2
from bs4 import BeautifulSoup

def gethtml(url):
    try:
        req = urllib2.Request(url)
        return urllib2.urlopen(req).read()
    except Exception, e:
        print 'Error Content Error'
        return ''

url = 'http://www.sunat.gob.pe/w/wapS01Alias?ruc=20428776110'
data = gethtml(url)
#print data
soup = BeautifulSoup(data)
#tag = soup.body.p.small
#print tag.small.contents[1].string
#tag= soup.select('p > small')
#print tag.contents[0]
#print tag.string
tag = soup.find_all('small')
for x in tag:
    # print x
    ts = BeautifulSoup(x.__str__())
    print ts.body.small.contents.__len__()
    print unicode(ts.body.small.contents[0].string)
    if ts.body.small.contents[0].string.startswith('Direcci'):
        print ts.body.small.contents[2]
#print tag

"""