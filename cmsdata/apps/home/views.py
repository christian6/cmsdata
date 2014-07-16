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
from django.core.exceptions import ObjectDoesNotExist
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
        context['document'] = Document.objects.all().order_by('description')
        context['operation'] = Operation.objects.all().order_by('description')
        date = datetime.datetime.today().date()
        context['exchange'] = Exchangerate.objects.filter(date=date)
        context['currency'] = Currency.objects.all().order_by('description')
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
                    phone = data['phone'].split('/')
                    data['phone'] = phone[0].strip()
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
                    print form
                    print 'form invalid'
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
        context['document'] = Document.objects.all().order_by('description')
        context['operation'] = Operation.objects.all().order_by('description')
        date = datetime.datetime.today().date()
        context['exchange'] = Exchangerate.objects.filter(date=date)
        context['currency'] = Currency.objects.all().order_by('description')
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
                # print form
                # print form.is_valid()
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

class ViewConstructInventory(TemplateView):
    template_name = 'home/construct.html'

    def get_context_data(self, **kwargs):
        context = super(ViewConstructInventory, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            context = {}
            try:
                if request.POST.get('type') == 'one':
                    obj = Inventory.register_materials('materials')
                    context['msg'] = obj
                elif request.POST.get('type') == 'all':
                    obj = Inventory.register_allinventory()
                print obj
                context['msg'] = obj
                context['status'] = obj
            except Exception, e:
                context['status'] = False
            return HttpResponse(simplejson.dumps(context), mimetype='application/json')

class ViewBedsideReport(TemplateView):
    template_name = 'home/bedsidereport.html'

    def get(self, request, *args, **kwargs):
        context = super(ViewBedsideReport, self).get_context_data(**kwargs)
        if request.is_ajax():
            # context = dict()
            try:
                months = {'01':'January','02':'February','03':'March','04':'April','05':'May','06':'June','07':'July','08':'August','09':'September','10':'October','11':'November','12':'Decembre'}
                month = Inventory.objects.values('month').filter(period__exact=request.GET.get('period')).distinct('month').order_by('month')
                context['months'] = [{'value':x['month'], 'month': months[x['month']]} for x in month]
                context['status'] = True
            except Exception, e:
                context['status'] = False
            return HttpResponse(simplejson.dumps(context), mimetype='application/json')
        context['period'] = [{'period': x['period']} for x in Inventory.objects.values('period').distinct('period').order_by('period')]
        return render_to_response(self.template_name, context, context_instance=RequestContext(request))

class ViewValued_Inventory(TemplateView):
    template_name = 'home/valued.html'

    def get_context_data(self, **kwargs):
        context = super(ViewValued_Inventory, self).get_context_data(**kwargs)
        return context

class ViewRptInventoryValued(TemplateView):
    def get(self, request, *args, **kwargs):
        return render_to_response('home/inventoryvalued.html', {}, context_instance=RequestContext(request))

import os
from django.conf import settings
import ho.pisa as pisa
import cStringIO as StringIO
import cgi

from django.template.loader import render_to_string

def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

def generate_pdf(html):
    # functions for generate the file PDF and return HttpResponse
    # pisa.showLogging(debug=True)
    result = StringIO.StringIO()
    #links = lambda uri, rel: os.path.join(settings.MEDIA_ROOT,uri.replace(settings.MEDIA_URL, ''))
    #print links
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode('UTF-8')), dest=result, link_callback=fetch_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype="application/pdf")
    return HttpResponse("error al generar el PDF: %s"%cgi.escape(html))
"""
   block generate pdf test
"""
def view_test_pdf(request):
    # view of poseable result pdf
    html = render_to_string('report/test.html',{'pagesize':'A4'},context_instance=RequestContext(request))
    return generate_pdf(html)
"""
    end block
"""

# Report document entry
class rpt_DocumentEntry(TemplateView):
    template_name = "home/rptentry.html"

    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            context['bedside'] = DocumentIn.objects.get(pk="%s%s"%(kwargs['entry'], kwargs['supplier']))
            context['details'] = DetDocumentIn.objects.filter(entry_id="%s%s"%(kwargs['entry'], kwargs['supplier']))
            html = render_to_string(self.template_name, context,context_instance=RequestContext(request))
            return generate_pdf(html)
        except ObjectDoesNotExist, e:
            return Http404(e)

# Report document outout
class rpt_DocumentOutput(TemplateView):
    template_name = "home/rptoutput.html"

    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            context['bedside'] = DocumentOut.objects.get(pk="%s%s"%(kwargs['output'], kwargs['customer']))
            context['details'] = DetDocumentOut.objects.filter(output_id="%s%s"%(kwargs['output'], kwargs['customer']))
            html = render_to_string(self.template_name, context,context_instance=RequestContext(request))
            return generate_pdf(html)
        except ObjectDoesNotExist, e:
            return Http404(e)

class rpt_InventoryValued(TemplateView):
    template_name = 'home/inventoryvalued.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        optiontwo = False
        try:
            namemonth = {'01':'Enero','02':'Febrero','03':'Marzo','04':'Abril','05':'Mayo','06':'Junio','07':'Julio','08':'Agosto','09':'Setiembre','10':'Octubre','11':'Noviembre','12':'Deciembre'}
            valued = []
            context['period'] = request.GET.get('period')
            matdetails = []
            if request.GET.get('type') == 'period':
                """ This section show in the report all the materials of period send as parameter """
                matdetails = Inventory.getMaterialsByPeriod(request.GET.get('period'))
            elif request.GET.get('type') == 'periodandmonth':
                matdetails = Inventory.getMaterialsByPeriodandMonth(request.GET.get('period'),request.GET.get('month'))
                optiontwo = True
            elif request.GET.get('type') == 'periodandmonthandmaterials':
                mat = request.GET.get('materials')[1:]
                matdetails = Inventory.getMaterialsByPerioandMonthandMaterials(request.GET.get('period'),request.GET.get('month'), mat)
                optiontwo = True
            elif request.GET.get('type') == 'periodandmaterials':
                mat = request.GET.get('materials')[1:]
                matdetails = Inventory.getMaterialsByPerioandMaterials(request.GET.get('period'), mat)

            matid = ''
            details = []
            counter = 0
            mes = ''
            months = []
            importendinit = 0
            quantityendinit = 0
            length = matdetails.__len__()
            # accumulate entry
            entrypriceaccum = 0
            entryimportaccum = 0
            entryquantityaccum = 0
            # accumulate ouput
            outputpriceaccum = 0
            outputquantityaccum = 0
            outputimportaccum = 0
            # accumulate saldo
            salpriceaccum = 0
            salquantityaccum = 0
            salimportaccum = 0
            for x in matdetails:
                if mes != '' and mes != x[1].strftime('%m'):
                    details.append({'months': months, 'monthname': namemonth[mes], 'entryquantityaccum': entryquantityaccum, 'entrypriceaccum': entrypriceaccum, 'entryimportaccum': entryimportaccum, 'outputquantityaccum':outputquantityaccum, 'outputpriceaccum': outputpriceaccum, 'outputimportaccum': outputimportaccum, 'salquantityaccum':salquantityaccum, 'salpriceaccum': salpriceaccum, 'salimportaccum': salimportaccum})
                    months = []
                    # accumulate entry
                    entrypriceaccum = 0
                    entryimportaccum = 0
                    entryquantityaccum = 0
                    # accumulate output
                    outputpriceaccum = 0
                    outputquantityaccum = 0
                    outputimportaccum = 0
                    # accumulate saldo
                    salpriceaccum = 0
                    salquantityaccum = 0
                    salimportaccum = 0
                if matid != '' and matid != x[2]:
                    if optiontwo:
                        details.append({'months': months, 'monthname': namemonth[mes], 'entryquantityaccum': entryquantityaccum, 'entrypriceaccum': entrypriceaccum, 'entryimportaccum': entryimportaccum, 'outputquantityaccum':outputquantityaccum, 'outputpriceaccum': outputpriceaccum, 'outputimportaccum': outputimportaccum, 'salquantityaccum':salquantityaccum, 'salpriceaccum': salpriceaccum, 'salimportaccum': salimportaccum})
                        months = []
                        # accumulate entry
                        entrypriceaccum = 0
                        entryimportaccum = 0
                        entryquantityaccum = 0
                        # accumulate output
                        outputpriceaccum = 0
                        outputquantityaccum = 0
                        outputimportaccum = 0
                        # accumulate saldo
                        salpriceaccum = 0
                        salquantityaccum = 0
                        salimportaccum = 0
                    materials = Materials.objects.get(pk=matid)
                    valued.append({'materials':materials.materiales_id, 'name': materials.matname, 'measure': materials.matmet, 'unit':materials.unit_id, 'details': details})
                    details = []

                if months.__len__() == 0:
                    year = x[1].strftime('%Y')
                    mon = x[1].strftime('%m')
                    if x[1].strftime('%m') == '01':
                        year = str(int(x[1].strftime('%Y')) - 1)
                        mon = '12'
                    init = Inventory.getSaldoonPeriodandMonth(materials=x[2], period=year, month=mon)
                    if init != []:
                        importendinit = (init[0][3] * init[0][4])
                        quantityendinit = init[0][3]
                        entryquantityaccum = (entryquantityaccum + quantityendinit)
                        entrypriceaccum = (entrypriceaccum + init[0][4])
                        entryimportaccum = (entryimportaccum + importendinit)
                        months.append({'quantity': quantityendinit, 'price': init[0][4], 'import': importendinit, 'endquantity':init[0][3], 'endprice':init[0][4], 'endimport': importendinit, 'type':'initial'})
                    else:
                        importendinit = 0
                        quantityendinit = 0
                        months.append({'quantity':0, 'price':0, 'import':0, 'endquantity':0, 'endprice':0, 'endimport':0, 'type':'initial'})

                pre = ''
                post = ''
                pre = x[0][:3]
                post = x[0][4:-11]
                if x[5] == 'ENTRY':
                    quantityendinit = (quantityendinit + x[3])
                    entryquantityaccum = (entryquantityaccum + x[3])
                    entrypriceaccum = (entrypriceaccum + x[4])
                    entryimportaccum = (entryimportaccum + (x[3] * x[4]))
                    months.append({'predoc':pre,'postdoc': post,'transfer':x[1].strftime('%d-%m-%Y'), 'doc':x[7], 'operation': x[6],'materials':x[2],'quantity':x[3],'price':x[4],'import':(x[3] * x[4]),'type':x[5], 'endquantity': quantityendinit, 'endprice': x[4], 'importend': (quantityendinit * x[4])})
                elif x[5] == 'OUTPUT':
                    quantityendinit = (quantityendinit - x[3])
                    outputquantityaccum = (outputquantityaccum + x[3])
                    outputpriceaccum = (outputpriceaccum + x[4])
                    outputimportaccum = (outputimportaccum + (x[3] * x[4]))
                    months.append({'predoc':pre,'postdoc': post,'transfer':x[1].strftime('%d-%m-%Y'), 'doc':x[7], 'operation': x[6],'materials':x[2],'quantity':x[3],'price':x[4],'import':(x[3] * x[4]),'type':x[5], 'endquantity': quantityendinit, 'endprice': x[4], 'importend': (quantityendinit * x[4])})
                # print x[1], x[2]
                counter += 1
                matid = x[2]
                mes = x[1].strftime('%m')
                # print length, counter
                if length == counter:
                    details.append({'months': months, 'monthname': namemonth[mes], 'entryquantityaccum': entryquantityaccum, 'entrypriceaccum': entrypriceaccum, 'entryimportaccum': entryimportaccum, 'outputquantityaccum':outputquantityaccum, 'outputpriceaccum': outputpriceaccum, 'outputimportaccum': outputimportaccum })
                    materials = Materials.objects.get(pk=matid)
                    valued.append({'materials':x[2], 'name': materials.matname, 'measure': materials.matmet, 'unit':materials.unit_id, 'details': details})

            context['inventory'] = valued
            #print context
            html = render_to_string(self.template_name, context, context_instance=RequestContext(request))
            return generate_pdf(html)
        except ObjectDoesNotExist, e:
            return Http404

"""
{'period': u'2013', 'inventory': [
    {'details': [
        {'months': [
            {'endquantity': 0, 'endimport': 0, 'endprice': 0, 'price': 0, 'import': 0, 'type': 'initial', 'quantity': 0},
            {'endquantity': 10.0, 'endprice': 20.0, 'price': 20.0, 'postdoc': u'00001201', 'predoc': u'001', 'importend': 200.0, 'transfer': '03-01-2013', 'materials': u'220018030014001', 'import': 200.0, 'type': u'ENTRY', 'quantity': 10.0},
            {'endquantity': 5.0, 'endprice': 22.0, 'price': 22.0, 'postdoc': u'00000266', 'predoc': u'001', 'importend': 110.0, 'transfer': '25-01-2013', 'materials': u'220018030014001', 'import': 110.0, 'type': u'OUTPUT', 'quantity': 5.0}
            ]
        },
        {'months': [
            {'endquantity': 5.0, 'endimport': 110.0, 'endprice': 22.0, 'price': 22.0, 'import': 110.0, 'type': 'initial', 'quantity': 5.0},
            {'endquantity': 25.0, 'endprice': 15.0, 'price': 15.0, 'postdoc': u'00001202', 'predoc': u'001', 'importend': 375.0, 'transfer': '15-02-2013', 'materials': u'220018030014001', 'import': 300.0, 'type': u'ENTRY', 'quantity': 20.0}
            ]
            },
        {'months': [
            {'endquantity': 25.0, 'endimport': 375.0, 'endprice': 15.0, 'price': 15.0, 'import': 375.0, 'type': 'initial', 'quantity': 25.0},
            {'endquantity': 55.0, 'endprice': 10.0, 'price': 10.0, 'postdoc': u'00001203', 'predoc': u'001', 'importend': 550.0, 'transfer': '20-03-2013', 'materials': u'220018030014001', 'import': 300.0, 'type': u'ENTRY', 'quantity': 30.0}
            ]
        },
        {'months': [
            {'endquantity': 55.0, 'endimport': 550.0, 'endprice': 10.0, 'price': 10.0, 'import': 550.0, 'type': 'initial', 'quantity': 55.0},
            {'endquantity': 63.0, 'endprice': 14.0, 'price': 14.0, 'postdoc': u'00001204', 'predoc': u'001', 'importend': 882.0, 'transfer': '24-04-2013', 'materials': u'220018030014001', 'import': 112.0, 'type': u'ENTRY', 'quantity': 8.0}
            ]
        },
        {'months': [
            {'endquantity': 63.0, 'endimport': 882.0, 'endprice': 14.0, 'price': 14.0, 'import': 882.0, 'type': 'initial', 'quantity': 63.0},
            {'endquantity': 155.0, 'endprice': 12.0, 'price': 12.0, 'postdoc': u'00001208', 'predoc': u'001', 'importend': 1860.0, 'transfer': '08-08-2013', 'materials': u'220018030014001', 'import': 1104.0, 'type': u'ENTRY', 'quantity': 92.0}
            ]
        },
        {'months': [
            {'endquantity': 155.0, 'endimport': 1860.0, 'endprice': 12.0, 'price': 12.0, 'import': 1860.0, 'type': 'initial', 'quantity': 155.0},
            {'endquantity': 170.0, 'endprice': 12.0, 'price': 12.0, 'postdoc': u'00001211', 'predoc': u'001', 'importend': 2040.0, 'transfer': '14-11-2013', 'materials': u'220018030014001', 'import': 180.0, 'type': u'ENTRY', 'quantity': 15.0}
            ]
        },
        {'months': [
            {'endquantity': 170.0, 'endimport': 2040.0, 'endprice': 12.0, 'price': 12.0, 'import': 2040.0, 'type': 'initial', 'quantity': 170.0},
            {'endquantity': 230.0, 'endprice': 12.0, 'price': 12.0, 'postdoc': u'00001212', 'predoc': u'001', 'importend': 2760.0, 'transfer': '19-12-2013', 'materials': u'220018030014001', 'import': 720.0, 'type': u'ENTRY', 'quantity': 60.0}
            ]
        }
    ], 'materials': u'220018030014001', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1"'},
    {'details': [
        {'months': [
            {'endquantity': 0, 'endimport': 0, 'endprice': 0, 'price': 0, 'import': 0, 'type': 'initial', 'quantity': 0},
            {'endquantity': 6.0, 'endprice': 30.0, 'price': 30.0, 'postdoc': u'00001201', 'predoc': u'001', 'importend': 180.0, 'transfer': '03-01-2013', 'materials': u'220018030014003', 'import': 180.0, 'type': u'ENTRY', 'quantity': 6.0}
            ]
        },
        {'months': [
            {'endquantity': 6.0, 'endimport': 180.0, 'endprice': 30.0, 'price': 30.0, 'import': 180.0, 'type': 'initial', 'quantity': 6.0},
            {'endquantity': 22.0, 'endprice': 20.0, 'price': 20.0, 'postdoc': u'00001202', 'predoc': u'001', 'importend': 440.0, 'transfer': '15-02-2013', 'materials': u'220018030014003', 'import': 320.0, 'type': u'ENTRY', 'quantity': 16.0}
        ]
        },
        {'months': [
            {'endquantity': 22.0, 'endimport': 440.0, 'endprice': 20.0, 'price': 20.0, 'import': 440.0, 'type': 'initial', 'quantity': 22.0},
            {'endquantity': 82.0, 'endprice': 8.9, 'price': 8.9, 'postdoc': u'00001203', 'predoc': u'001', 'importend': 729.8000000000001, 'transfer': '20-03-2013', 'materials': u'220018030014003', 'import': 534.0, 'type': u'ENTRY', 'quantity': 60.0}
            ]
        },
        {'months': [
            {'endquantity': 82.0, 'endimport': 729.8000000000001, 'endprice': 8.9, 'price': 8.9, 'import': 729.8000000000001, 'type': 'initial', 'quantity': 82.0},
            {'endquantity': 95.0, 'endprice': 9.0, 'price': 9.0, 'postdoc': u'00001204', 'predoc': u'001', 'importend': 855.0, 'transfer': '24-04-2013', 'materials': u'220018030014003', 'import': 117.0, 'type': u'ENTRY', 'quantity': 13.0}
        ]
        },
        {'months': [
            {'endquantity': 95.0, 'endimport': 855.0, 'endprice': 9.0, 'price': 9.0, 'import': 855.0, 'type': 'initial', 'quantity': 95.0},
            {'endquantity': 141.0, 'endprice': 13.0, 'price': 13.0, 'postdoc': u'00001208', 'predoc': u'001', 'importend': 1833.0, 'transfer': '08-08-2013', 'materials': u'220018030014003', 'import': 598.0, 'type': u'ENTRY', 'quantity': 46.0}
            ]
        }
        ], 'materials': u'220018030014003', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/2"'}
    ]
}


{'period': u'2013', 'inventory': [
    {'details': [], 'materials': u'220018030014001', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1"'},
    {'details': [
        {'months': [
          {'endquantity': 0, 'endimport': 0, 'endprice': 0, 'price': 0, 'import': 0, 'type': 'initial', 'quantity': 0},
          {'endquantity': 10.0, 'endprice': 20.0, 'price': 20.0, 'postdoc': u'00001201', 'predoc': u'001', 'importend': 200.0, 'transfer': '03-01-2013', 'materials': u'220018030014001', 'import': 200.0, 'type': u'ENTRY', 'quantity': 10.0},
          {'endquantity': 5.0, 'endprice': 22.0, 'price': 22.0, 'postdoc': u'00000266', 'predoc': u'001', 'importend': 110.0, 'transfer': '25-01-2013', 'materials': u'220018030014001', 'import': 110.0, 'type': u'OUTPUT', 'quantity': 5.0},
          {'endquantity': 11.0, 'endprice': 30.0, 'price': 30.0, 'postdoc': u'00001201', 'predoc': u'001', 'importend': 330.0, 'transfer': '03-01-2013', 'materials': u'220018030014003', 'import': 180.0, 'type': u'ENTRY', 'quantity': 6.0}], 'monthname': 'January'}
        ], 'materials': u'220018030014003', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/2"'}
    ]
}

"""