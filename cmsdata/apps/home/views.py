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

from .forms import *

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

