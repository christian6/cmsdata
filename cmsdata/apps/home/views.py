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

class rpt_InventoryValued(TemplateView):
    template_name = 'home/inventoryvalued.html'

    def get(self, request, *args, **kwargs):
        context = dict()
        try:
            valued = []
            if request.GET.get('type') == 'period':
                """ This section show in the report all the materials of period send as parameter """
                context['period'] = request.GET.get('period')
                matdetails = Inventory.getMaterialsByPeriod(request.GET.get('period'))
                matid = ''
                details = []
                counter = 0
                length = matdetails.__len__()
                for x in matdetails:
                    if matid != '' and matid != x[2]:
                        materials = Materials.objects.get(pk=matid)
                        valued.append({'materials':materials.materiales_id, 'name': materials.matname, 'measure': materials.matmet, 'unit':materials.unit_id, 'details': details})
                        details = []
                    if details.__len__() == 0:
                        if x[1].strftime('%m') == '01':
                            init = Inventory.objects.filter(materials_id=x[2], period=str(int(x[1].strftime('%Y')) - 1)).order_by('period','-month')
                        else:
                            init = Inventory.objects.filter(materials_id=x[2], period=x[1].strftime('%Y')).order_by('-month')
                        for x in init:
                            if :
                                pass
                        details.append({'quantity':0, 'price':0, 'import':0, 'endquantity':0, 'endprice':0, 'endimport':0, 'type':'initial'})
                    pre = ''
                    post = ''
                    pre = x[0][:3]
                    post = x[0][4:-11]
                    details.append({'predoc':pre,'postdoc': post,'transfer':x[1].strftime('%d-%m-%Y'),'materials':x[2],'quantity':x[3],'price':x[4],'impor':(x[3] * x[4]),'type':x[5]})
                    print x[1], x[2]
                    counter += 1
                    matid = x[2]
                    print length, counter
                    if length == counter:
                        materials = Materials.objects.get(pk=matid)
                        valued.append({'materials':x[2], 'name': materials.matname, 'measure': materials.matmet, 'unit':materials.unit_id, 'details': details})

            context['inventory'] = valued
            print context
            html = render_to_string(self.template_name, context, context_instance=RequestContext(request))
            return generate_pdf(html)
        except ObjectDoesNotExist, e:
            return Http404

"""
{
valued: [
        { materials: 105405, name: 'abrazadera', measure: '1 x 1"', details: [
                                                                            {transfer: '06/01/2013',quantity:10,price:2,type:'entry'},
                                                                            {transfer: '09/01/2013',quantity:10,price:2,type:'entry'},
                                                                            {transfer: '15/01/2013',quantity:10,price:2,type:'output'},
                                                                            {transfer: '26/01/2013',quantity:10,price:2,type:'entry'}
                                                                            ]
        },
        { materials: 105406, name: 'abrazadera', measure: '1 x 2"', details: [
                                                                            {transfer: '02/01/2013',quantity:10,price:2,type:'entry'}
                                                                            ]
        },
    ]
}
{'period': u'2013', 'inventory': [
{'details': [
    {'transfer': '03-01-2013', 'price': 12.3, 'materials': u'220018030014001', 'postdoc': u'00006565', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 60.0},
    {'transfer': '18-01-2013', 'price': 11.3, 'materials': u'220018030014001', 'postdoc': u'00001202', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 10.0},
    {'transfer': '16-09-2013', 'price': 8.9, 'materials': u'220018030014001', 'postdoc': u'00001203', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 12.0},
    {'transfer': '08-11-2013', 'price': 10.5, 'materials': u'220018030014001', 'postdoc': u'00001211', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 30.0}
], 'materials': u'220018030014002', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/4"'},
{'details': [
    {'transfer': '03-01-2013', 'price': 10.2, 'materials': u'220018030014002', 'postdoc': u'00006565', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 12.0},
    {'transfer': '18-01-2013', 'price': 9.6, 'materials': u'220018030014002', 'postdoc': u'00001202', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 15.0},
    {'transfer': '16-09-2013', 'price': 8.9, 'materials': u'220018030014002', 'postdoc': u'00001203', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 22.0}
], 'materials': u'220018030014003', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/2"'}
]
}

{'period': u'2013', 'inventory': [
    {'details': [
        {'transfer': '03-01-2013', 'price': 12.3, 'materials': u'220018030014001', 'postdoc': u'00006565', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 60.0},
        {'transfer': '18-01-2013', 'price': 11.3, 'materials': u'220018030014001', 'postdoc': u'00001202', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 10.0},
        {'transfer': '16-09-2013', 'price': 8.9, 'materials': u'220018030014001', 'postdoc': u'00001203', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 12.0},
        {'transfer': '08-11-2013', 'price': 10.5, 'materials': u'220018030014001', 'postdoc': u'00001211', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 30.0}
        ], 'materials': u'220018030014002', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/4"'},
    {'details': [
        {'transfer': '03-01-2013', 'price': 10.2, 'materials': u'220018030014002', 'postdoc': u'00006565', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 12.0},
        {'transfer': '18-01-2013', 'price': 9.6, 'materials': u'220018030014002', 'postdoc': u'00001202', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 15.0},
        {'transfer': '16-09-2013', 'price': 8.9, 'materials': u'220018030014002', 'postdoc': u'00001203', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 22.0}
        ],'materials': u'220018030014002', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/4"'},
    {'details': [
        {'transfer': '03-01-2013', 'price': 10.2, 'materials': u'220018030014002', 'postdoc': u'00006565', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 12.0},
        {'transfer': '18-01-2013', 'price': 9.6, 'materials': u'220018030014002', 'postdoc': u'00001202', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 15.0},
        {'transfer': '16-09-2013', 'price': 8.9, 'materials': u'220018030014002', 'postdoc': u'00001203', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 22.0}
    ], 'materials': u'220018030014003', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/2"'}]}

{'period': u'2013', 'inventory': [
    {'details': [
        {'transfer': '03-01-2013', 'price': 12.3, 'materials': u'220018030014001', 'postdoc': u'00006565', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 60.0},
        {'transfer': '18-01-2013', 'price': 11.3, 'materials': u'220018030014001', 'postdoc': u'00001202', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 10.0},
        {'transfer': '16-09-2013', 'price': 8.9, 'materials': u'220018030014001', 'postdoc': u'00001203', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 12.0},
        {'transfer': '08-11-2013', 'price': 10.5, 'materials': u'220018030014001', 'postdoc': u'00001211', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 30.0}
        ], 'materials': u'220018030014002', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/4"'}, 
    {'details': [
        {'transfer': '03-01-2013', 'price': 10.2, 'materials': u'220018030014002', 'postdoc': u'00006565', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 12.0},
        {'transfer': '18-01-2013', 'price': 9.6, 'materials': u'220018030014002', 'postdoc': u'00001202', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 15.0}, 
        {'transfer': '16-09-2013', 'price': 8.9, 'materials': u'220018030014002', 'postdoc': u'00001203', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 22.0}
        ], 'materials': u'220018030014003', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/2"'},
    {'details': [
    {'transfer': '08-11-2013', 'price': 8.6, 'materials': u'220018030014003', 'postdoc': u'00001211', 'type': u'ENTRY', 'predoc': u'001', 'quantity': 16.0}
    ], 'materials': u'220018030014003', 'name': u'Abrazadera Fig. 1000', 'unit': u'Unid', 'measure': u' 1" x 1 1/2"'}
]
}
"""