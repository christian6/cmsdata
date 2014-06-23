#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_list_or_404
from django.views.generic.base import TemplateView, View
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.template import RequestContext
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.urlresolvers import reverse
from django.db.models import Count

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
                    message = "Usuario o Password invalid!"
            else:
                message = "Usuario o Password, invalid!"
                context = { 'form': logininForm(), 'msg': message }
            return render_to_response('home/login.html', context, context_instance=RequestContext(request))
        except Exception, e:
            raise Http404("Method no proccess")

class ViewLogout(View):
    def get(self, request, *args, **kwargs):
        logout(self.request)
        return HttpResponseRedirect(reverse('view_login'))

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
        if request.GET.get('search') is not None:
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
    def get(self, request, *args, **kwargs):
        if request.GET.get('serie') is not None:
            obj = DocumentIn.objects.get(pk__exact="%s%s"%(request.GET.get('serie'),request.GET.get('ruc')))
            if obj.status == 'CO':
                return HttpResponseRedirect(reverse('view_add_docin'))
        context = super(ViewDocumentIn, self).get_context_data(**kwargs)
        context['serie'] = '' if request.GET.get('serie') is None else request.GET.get('serie')
        context['new'] = '1' if request.GET.get('new') is None else '0'
        context['details'] = '1' if request.GET.get('details') is not None else '0'
        context['ruc'] = '' if request.GET.get('ruc') is None else request.GET.get('ruc')
        return render_to_response(self.template_name, context, context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                # valid ruc supplier
                counter = Supplier.objects.filter(pk=request.POST.get('supplier')).aggregate(Count=Count('supplier_id'))
                if counter['Count'] == 0:
                    # request Data json
                    data = json.loads(request.POST.get('data_s'))
                    data['flag'] = True
                    data['supplier_id'] = data['ruc']
                    form = addSupplierForm(data)
                    if form.is_valid():
                        form.save()
                form = addDocumentInForm(request.POST)
                if form.is_valid():
                    add = form.save(commit=False)
                    add.status = 'PE'
                    add.flag = True
                    add.save()
                    context['status'] = True
                    context['serie'] = request.POST.get('serie')
                    context['ruc'] = request.POST.get('supplier')
                else:
                    context['status'] = False
            except Exception, e:
                print e
                context['status'] = False
            return HttpResponse(simplejson.dumps(context), mimetype='application/json')


class ViewDocumentOut(TemplateView):
    template_name = "home/documentout.html"

    def get(self, request, *args, **kwargs):
        if request.GET.get('serie') is not None:
            obj = DocumentOut.objects.get(output_id__exact="%s%s"%(request.GET.get('serie'),request.GET.get('ruc')))
            if obj.status == 'CO':
                return HttpResponseRedirect(reverse('view_add_docout'))
        context = super(ViewDocumentOut, self).get_context_data(**kwargs)
        context['serie'] = '' if request.GET.get('serie') is None else request.GET.get('serie')
        context['new'] = '1' if request.GET.get('new') is None else '0'
        context['details'] = '1' if request.GET.get('details') is not None else '0'
        context['ruc'] = '' if request.GET.get('ruc') is None else request.GET.get('ruc')
        return render_to_response(self.template_name, context, context_instance=RequestContext(request))

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                # valid ruc supplier
                counter = Customer.objects.filter(pk=request.POST.get('customers')).aggregate(Count=Count('customers_id'))
                if counter['Count'] == 0:
                    print "registra nuevo cliente"
                    # request Data json
                    data = json.loads(request.POST.get('data_s'))
                    data['flag'] = True
                    data['customers_id'] = data['ruc']
                    form = addCustomerForm(data)
                    if form.is_valid():
                        form.save()
                form = addDocumentOutForm(request.POST)
                print form
                print form.is_valid()
                if form.is_valid():
                    add = form.save(commit=False)
                    add.status = 'PE'
                    add.flag = True
                    add.save()
                    context['status'] = True
                    context['serie'] = request.POST.get('serie')
                    context['ruc'] = request.POST.get('customers')
                else:
                    context['status'] = False
            except Exception, e:
                context['status'] = False
            return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class ViewListDocumentOutput(TemplateView):
    template_name = "home/listdocoutput.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = super(ViewListDocumentOutput, self).get_context_data(**kwargs)
        if request.GET.get('search') is not None:
            if request.GET.get('search') == 'status':
                model = DocumentOut.objects.filter(flag=True, status=request.GET.get('status'))
            else:
                if request.GET.get('dend') == '' :
                    model = DocumentOut.objects.filter(flag=True, transfer=request.GET.get('dstart'))
                else:
                    model = DocumentOut.objects.filter(flag=True, transfer__range=(request.GET.get('dstart'), request.GET.get('dend')) )
        else:
            model = DocumentOut.objects.filter(flag=True, status='PE')

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

class ViewMaterials(TemplateView):
    template_name = "home/documentin.html"

class ViewSupplier(TemplateView):
    template_name = "home/documentin.html"

class ViewSearchMaterialsPrice(TemplateView):
    template_name = "home/consultmaterials.html"