import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db import connection, transaction


class Currency(models.Model):
    currency_id = models.CharField(primary_key=True, max_length=2)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s - %s"%(self.currency_id, self.description)

class Exchangerate(models.Model):
    currency = models.ForeignKey(Currency, to_field='currency_id')
    purchase = models.FloatField()
    sale = models.FloatField()
    date = models.DateField(auto_now=True)
    register = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return ""%(self.currency, self.purchase, self.sale, self.date)

class Document(models.Model):
    document_id = models.CharField(primary_key=True, max_length=2)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s"%(self.document_id, self.description)

class Operation(models.Model):
    operation_id = models.CharField(primary_key=True, max_length=2)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s - %s"%(self.operation_id, self.description)

class Supplier(models.Model):
    supplier_id = models.CharField(primary_key=True, max_length=11)
    reason = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=11)
    flag = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s %s"%(self.supplier_id, self.reason)

class Unit(models.Model):
    unit_id = models.CharField(primary_key=True, max_length=7)
    unit = models.CharField(max_length=11)
    flag = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s %s"%(self.unit_id, self.unit)

class Materials(models.Model):
    materiales_id = models.CharField(primary_key=True, max_length=15)
    matname = models.CharField(max_length=200)
    matmet = models.CharField(max_length=200)
    unit = models.ForeignKey(Unit, to_field='unit_id')
    flag = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s %s"%(self.materiales_id, self.matname)

class Customer(models.Model):
    customers_id = models.CharField(primary_key=True, max_length=11)
    reason = models.CharField(max_length=220)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=11)
    flag = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s %s"%(self.customers_id, self.reason)


class DocumentIn(models.Model):
    entry_id = models.CharField(primary_key=True, max_length=23)
    serie = models.CharField(max_length=12)
    supplier = models.ForeignKey(Supplier)
    destination = models.CharField(max_length=200)
    document = models.ForeignKey(Document, to_field='document_id', default='01', null=True)
    operation = models.ForeignKey(Operation, to_field='operation_id', default='01', null=True)
    register = models.DateTimeField(auto_now=True)
    transfer = models.DateField(null=True)
    reference = models.CharField(max_length=160, null=True, blank=True)
    motive = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=2, default='PE')
    flag = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s %s %s %s"%(self.entry_id, self.serie, self.supplier_id, self.transfer)

class DetDocumentIn(models.Model):
    entry = models.ForeignKey(DocumentIn, to_field='entry_id')
    materials = models.ForeignKey(Materials, to_field='materiales_id')
    quantity = models.FloatField()
    price = models.FloatField()
    flag = models.BooleanField(default=True)

    @property
    def amount(self):
        return self.quantity * self.price

    def __unicode__(self):
        return "%s %s %f %f"%(self.entry, self.materials, self.quantity, self.price)

class DocumentOut(models.Model):
    output_id = models.CharField(primary_key=True, max_length=23)
    serie = models.CharField(max_length=12)
    customers = models.ForeignKey(Customer, to_field='customers_id')
    reason = models.CharField(max_length=200)
    document = models.ForeignKey(Document, to_field='document_id', default='01', null=True)
    operation = models.ForeignKey(Operation, to_field='operation_id', default='01', null=True)
    startpoint = models.CharField(max_length=200)
    endpoint = models.CharField(max_length=200)
    register = models.DateTimeField(auto_now=True)
    transfer = models.DateField()
    transruc = models.CharField(max_length=11, null=True, blank=True)
    transreason = models.CharField(max_length=200, null=True, blank=True)
    plate = models.CharField(max_length=7, null=True, blank=True)
    license = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=2, default='PE')
    flag = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s %s %s %s"%(self.output_id, self.serie, self.customers, self.transfer)

class DetDocumentOut(models.Model):
    output = models.ForeignKey(DocumentOut, to_field='output_id')
    materials = models.ForeignKey(Materials, to_field='materiales_id')
    quantity = models.FloatField()
    price = models.FloatField()
    flag = models.BooleanField(default=True)

    @property
    def amount(self):
        return self.quantity * self.price

    def __unicode__(self):
        return "%s %s %f %f"%(self.output, self.materials, self.quantity, self.price)
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
    ]
class Inventory(models.Model):
    period = models.CharField(max_length=4)
    register = models.DateField(auto_now=True)
    month = models.CharField(max_length=2)
    materials = models.ForeignKey(Materials, to_field='materiales_id')
    quantity = models.FloatField()
    price = models.FloatField()
    exists = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s %s %s %f %f'%(self.period, self.month, self.materials, self.quantity, self.price)

    @staticmethod
    @transaction.commit_on_success
    def register_materials(materials):
        try:
            cn = connection.cursor() # Open connection to DDBB
            cn.callproc('sp_constructinventory',[materials,]) # Execute Store Procedure
            result = cn.fetchone() # recover result
            cn.close() # close connection
            return result[0]
        except Exception, e:
            transaction.rollback()
            return False

    @staticmethod
    @transaction.commit_on_success
    def register_allinventory():
        try:
            cn = connection.cursor() # Open connection to DDBB
            cn.callproc('sp_constructallmaterials') # Execute Store Procedure
            result = cn.fetchone() # recover result
            cn.close() # close connection
            return result[0]
        except Exception, e:
            transaction.rollback()
            return False

    @staticmethod
    @transaction.commit_on_success
    def getBymaterialsPeriodMonth(materials='', period='', month=''):
        try:
            cn = connection.cursor() # Open connection to DDBB
            #cn.execute("select * from spconsultbymaterialperiodmonth_inventory('%s','%s','%s')"%(materials, period, month))
            cn.callproc('spconsultbymaterialperiodmonth_inventory',[materials, period, month,])
            #result = dictfetchall(cn) # recover result
            result = []
            pre = ''
            post = ''
            for x in cn.fetchall():
                # ruc = x[0][-11:]
                pre = x[0][:3]
                post = x[0][4:-11]
                result.append({'predoc':pre,'postdoc': post,'transfer':x[1].strftime('%d-%m-%Y'),'materials':x[2],'quantity':x[3],'price':x[4],'type':x[5]})
            cn.close() # close connection
            return result
        except Exception, e:
            print e
            transaction.rollback()
            return False

    @staticmethod
    @transaction.commit_on_success
    def getMaterialsByPeriod(period=''):
        try:
            cn = connection.cursor()
            cn.callproc('sp_rpt_consultdetailsbyperiod',[period])
            result = cn.fetchall() #
            cn.close() # close connection
            return result
        except BaseException:
            transaction.rollback()
            return False

    @staticmethod
    @transaction.commit_on_success
    def getMaterialsByPeriodandMonth(period='', month=''):
        try:
            cn = connection.cursor()
            cn.callproc('sp_rpt_consultdetailsbyperiodandmonth', [period, month])
            result = cn.fetchall()
            cn.close()
            return result
        except Exception, e:
            raise e
            transaction.rollback()

    @staticmethod
    @transaction.commit_on_success
    def getMaterialsByPerioandMonthandMaterials(period='',month='',materials=''):
        try:
            cn = connection.cursor()
            cn.execute("select * from home_construct where to_char(transfer, 'YYYY') like '%s' and to_char(transfer, 'MM') like '%s' and materials_id IN (%s) order by materials_id, transfer asc"%(period, month,materials))
            result = cn.fetchall()
            cn.close()
            return result
        except Exception, e:
            raise e
            transaction.rollback()

    @staticmethod
    @transaction.commit_on_success
    def getMaterialsByPerioandMaterials(period='', materials=''):
        try:
            cn = connection.cursor()
            cn.execute("select * from home_construct where to_char(transfer, 'YYYY') like '%s' and materials_id IN (%s) order by materials_id, transfer asc"%(period,materials))
            result = cn.fetchall()
            cn.close()
            return result
        except Exception, e:
            raise e
            transaction.rollback()

    @staticmethod
    @transaction.commit_on_success
    def getSaldoonPeriodandMonth(period='',month='',materials=''):
        try:
            cn = connection.cursor()
            cn.callproc('sp_reportsaldo',[period, month, materials])
            result = cn.fetchall()
            cn.close()
            return result
        except Exception, e:
            transaction.rollback()

class userProfile(models.Model):
    user = models.OneToOneField(User)
    empdni = models.CharField(max_length=8,null=False)
    # cargo = models.ForeignKey(Cargo, to_field='cargo_id', null=True)
    # photo = models.ImageField(upload_to=url,null=True, blank=True)

    # def url(self,filename):
    #     ruta = "MutimediaData/Users/%s/%s"%(self.user.username,filename)
    #     return ruta

    def __unicode__(self):
        return self.user.username
