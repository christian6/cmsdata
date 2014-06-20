from django.db import models
from django.contrib.auth.models import User

# Create your models here.

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

    # class Meta:
    #     verbose_name = _('Unit')
    #     verbose_name_plural = _('Units')

    def __unicode__(self):
        return "%s %s"%(self.unit_id, self.unit)

class Materials(models.Model):
    materiales_id = models.CharField(primary_key=True, max_length=15)
    matname = models.CharField(max_length=200)
    matmet = models.CharField(max_length=200)
    unit = models.ForeignKey(Unit, to_field='unit_id')
    flag = models.BooleanField(default=True)

    # class Meta:
    #     verbose_name = _('Materials')
    #     verbose_name_plural = _('Materialss')

    def __unicode__(self):
        return "%s %s"%(self.materiales_id, self.matname)

class Customer(models.Model):
    custormers_id = models.CharField(primary_key=True, max_length=11)
    reason = models.CharField(max_length=220)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=11)
    flag = models.BooleanField(default=True)

    # class Meta:
    #     verbose_name = _('Customer')
    #     verbose_name_plural = _('Customers')

    def __unicode__(self):
        return "%s %s"%(self.custormers_id, self.reason)
    

class DocumentIn(models.Model):
    serie_id = models.CharField(primary_key=True, max_length=12)
    supplier = models.ForeignKey(Supplier)
    destination = models.CharField(max_length=200)
    register = models.DateTimeField(auto_now=True)
    transfer = models.DateField(null=True)
    reference = models.CharField(max_length=160, null=True, blank=True)
    motive = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=2, default='PE')
    flag = models.BooleanField(default=True)

    # class Meta:
    #     verbose_name = _('DocumentIn')
    #     verbose_name_plural = _('DocumentIns')

    def __unicode__(self):
        return "%s %s %s"%(self.serie_id, self.supplier_id, self.transfer)

class DetDocumentIn(models.Model):
    serie = models.ForeignKey(DocumentIn, to_field='serie_id')
    materials = models.ForeignKey(Materials, to_field='materiales_id')
    quantity = models.FloatField()
    price = models.FloatField()
    flag = models.BooleanField(default=True)

    # class Meta:
    #     verbose_name = _('DetDocumentin')
    #     verbose_name_plural = _('DetDocumentins')

    def __unicode__(self):
        return "%s %s %f %f"%(self.serie, self.materials, self.quantity, self.price)

# class tmpinput(models.Model):
#     token = models.CharField(max_length=8)
#     materials = models.ForeignKey(Materials, to_field='materiales_id')
#     quantity = models.FloatField()
#     price = models.FloatField()

class DocumentOut(models.Model):
    serie_id = models.CharField(primary_key=True, max_length=11)
    custormers = models.ForeignKey(Customer, to_field='custormers_id')
    reason = models.CharField(max_length=200)
    startpoint = models.CharField(max_length=200)
    endpoint = models.CharField(max_length=200)
    register = models.DateTimeField(auto_now=True)
    transfer = models.DateField()
    transruc = models.CharField(max_length=11, null=True, blank=True)
    transreason = models.CharField(max_length=200, null=True, blank=True)
    plate = models.CharField(max_length=7, null=True, blank=True)
    license = models.CharField(max_length=10)
    status = models.CharField(max_length=2, default='PE')
    flag = models.BooleanField(default=True)

    # class Meta:
    #     verbose_name = _('DocumentOut')
    #     verbose_name_plural = _('DocumentOuts')

    def __unicode__(self):
        return "%s %s %s"%(self.serie_id, self.custormers, self.transfer)

class DetDocumentOut(models.Model):
    serie = models.ForeignKey(DocumentOut, to_field='serie_id')
    materials = models.ForeignKey(Materials, to_field='materiales_id')
    quantity = models.FloatField()
    price = models.FloatField()
    flag = models.BooleanField(default=True)

    # class Meta:
    #     verbose_name = _('DetDocumentOut')
    #     verbose_name_plural = _('DetDocumentOuts')

    def __unicode__(self):
        return "%s %s %f %f"%(self.serie, self.materials, self.quantity, self.price)

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